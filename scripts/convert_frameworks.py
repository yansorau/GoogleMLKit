#!/usr/bin/env python3
"""Package the pinned official ML Kit frameworks for device and Apple silicon simulator."""

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import struct
import subprocess
import tempfile


MODULES = {
    "MLKitCommon": {
        "version": "14.0.0",
        "source": "https://dl.google.com/dl/cpdc/00f258dabdb58dfa/MLKitCommon-14.0.0.tar.gz",
        "sha256": "ee588e0b1bd6ca6f455001d59e769396ab40566acdd5001f85c54df24e487c54",
    },
    "MLKitLanguageID": {
        "version": "9.0.0",
        "source": "https://dl.google.com/dl/cpdc/abd494a0381d8d03/MLKitLanguageID-9.0.0.tar.gz",
        "sha256": "4a05208e7881d3fcf0725ec8a3813b7a1a0afb5343e1089d2a118a343134c372",
    },
    "MLKitNaturalLanguage": {
        "version": "10.0.0",
        "source": "https://dl.google.com/dl/cpdc/16c4bb76b6337f56/MLKitNaturalLanguage-10.0.0.tar.gz",
        "sha256": "03677e13dd1071140cd24f1eebabd44df6a7ab2369aca62475780b27ac92e632",
    },
}
MACHO_64 = b"\xcf\xfa\xed\xfe"
LC_BUILD_VERSION = 0x32
CPU_TYPE_ARM64 = 0x100000C


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)


def objects(data):
    """Yield member byte ranges without extraction, preserving duplicate names and the ar index."""
    if data[:4] == MACHO_64:
        yield "Mach-O", 0, len(data)
        return
    require(data[:8] == b"!<arch>\n", "Expected a thin Mach-O object or static archive")
    offset = 8
    while offset < len(data):
        header = data[offset:offset + 60]
        require(len(header) == 60 and header[58:60] == b"`\n", "Invalid ar member header")
        size = int(header[48:58])
        start, end = offset + 60, offset + 60 + size
        require(end <= len(data), "Truncated ar member")
        name = header[:16].decode("ascii").strip()
        if name.startswith("#1/"):
            name_size = int(name[3:])
            require(name_size <= size, "Invalid extended ar member name")
            name = data[start:start + name_size].rstrip(b"\0").decode("utf-8")
            start += name_size
        if data[start:start + 4] == MACHO_64:
            yield name, start, end
        else:
            require(name.startswith("__.SYMDEF") or name in ("/", "//"),
                    f"Unsupported non-Mach-O archive member: {name}")
        offset = end + size % 2
    require(offset == len(data), "Invalid archive padding")


def platform_fields(data):
    found = []
    for name, start, end in objects(data):
        magic, cpu, _, file_type, ncmds, sizeofcmds = struct.unpack_from("<IiiIII", data, start)
        require(cpu == CPU_TYPE_ARM64 and file_type == 1, f"{name}: expected arm64 MH_OBJECT")
        position, limit = start + 32, start + 32 + sizeofcmds
        require(limit <= end, f"{name}: truncated load commands")
        versions = []
        for _ in range(ncmds):
            require(position + 8 <= limit, f"{name}: truncated load command")
            command, size = struct.unpack_from("<II", data, position)
            require(size >= 8 and position + size <= limit, f"{name}: invalid load command size")
            if command == LC_BUILD_VERSION:
                require(size >= 24, f"{name}: invalid LC_BUILD_VERSION")
                versions.append(position + 8)
            position += size
        require(position == limit and len(versions) == 1,
                f"{name}: expected exactly one LC_BUILD_VERSION")
        found.append((name, versions[0]))
    require(found, "No Mach-O objects found")
    return found


def convert(data):
    fields = platform_fields(data)
    converted = bytearray(data)
    for name, offset in fields:
        require(struct.unpack_from("<I", data, offset)[0] == 2, f"{name}: expected iOS platform")
        struct.pack_into("<I", converted, offset, 7)
    converted = bytes(converted)
    # Reverse only the platform patches and compare every byte, including archive indexes,
    # load command version fields, code, relocations, symbol tables, and member padding.
    restored = bytearray(converted)
    for name, offset in platform_fields(converted):
        require(struct.unpack_from("<I", converted, offset)[0] == 7,
                f"{name}: simulator platform conversion failed")
        struct.pack_into("<I", restored, offset, 2)
    require(bytes(restored) == data, "Conversion changed bytes outside platform fields")
    names = collections.Counter(name for name, _ in fields)
    return converted, len(fields), sum(count - 1 for count in names.values())


def framework(source, destination, name, binary, version, simulator):
    shutil.copytree(source, destination)
    (destination / name).write_bytes(binary)
    info_path = destination / "Info.plist"
    info = plistlib.loads(info_path.read_bytes()) if info_path.exists() else {}
    info.update({
        "CFBundleExecutable": name,
        "CFBundleIdentifier": "com.google.mlkit." + name.lower(),
        "CFBundleName": name,
        "CFBundlePackageType": "FMWK",
        "CFBundleShortVersionString": version,
        "CFBundleVersion": version,
        "MinimumOSVersion": "15.5",
        "CFBundleSupportedPlatforms": ["iPhoneSimulator" if simulator else "iPhoneOS"],
    })
    info_path.write_bytes(plistlib.dumps(info))


def publish(staged, root, paths, backup):
    """Replace only validated artifacts and restore previous artifacts on a publication error."""
    changed = []
    try:
        for name in paths:
            target, old = root / name, backup / name
            had_old = target.exists()
            if had_old:
                os.replace(target, old)
            changed.append((target, old, had_old))
            os.replace(staged / name, target)
    except BaseException:
        for target, old, had_old in reversed(changed):
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
            if had_old:
                os.replace(old, target)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True,
                        help="Directory containing MODULE/Frameworks/MODULE.framework from official SDKs")
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".conversion-", dir=root) as temporary:
        work = Path(temporary)
        staged, backup = work / "output", work / "backup"
        staged.mkdir()
        backup.mkdir()
        manifest = {}
        for name, metadata in MODULES.items():
            sdk = args.source_root.resolve() / name
            source = sdk / "Frameworks" / (name + ".framework")
            original = (source / name).read_bytes()
            require(sha256(original) == metadata["sha256"], f"{name}: unexpected official binary checksum")
            module_work = work / name
            module_work.mkdir()
            device, intel = module_work / "device.bin", module_work / "x86_64.bin"
            run("xcrun", "lipo", "-thin", "arm64", source / name, "-output", device)
            run("xcrun", "lipo", "-thin", "x86_64", source / name, "-output", intel)
            arm64_device, x86_64_simulator = device.read_bytes(), intel.read_bytes()
            arm64_simulator, count, duplicates = convert(arm64_device)
            converted = module_work / "arm64-simulator.bin"
            converted.write_bytes(arm64_simulator)
            universal = module_work / "simulator.bin"
            run("xcrun", "lipo", "-create", converted, intel, "-output", universal)
            device_framework = module_work / "device" / (name + ".framework")
            simulator_framework = module_work / "simulator" / (name + ".framework")
            framework(source, device_framework, name, arm64_device, metadata["version"], False)
            framework(source, simulator_framework, name, universal.read_bytes(), metadata["version"], True)
            output = staged / (name + ".xcframework")
            run("xcodebuild", "-create-xcframework", "-framework", device_framework,
                "-framework", simulator_framework, "-output", output)
            info = plistlib.loads((output / "Info.plist").read_bytes())
            libraries = {entry["LibraryIdentifier"]: entry for entry in info["AvailableLibraries"]}
            require(set(libraries) == {"ios-arm64", "ios-arm64_x86_64-simulator"},
                    f"{name}: unexpected XCFramework slices")
            for identifier, architectures in [("ios-arm64", {"arm64"}),
                                               ("ios-arm64_x86_64-simulator", {"arm64", "x86_64"})]:
                entry = libraries[identifier]
                require(entry["SupportedPlatform"] == "ios" and set(entry["SupportedArchitectures"]) == architectures,
                        f"{name}: incorrect slice platform or architectures")
                expected_variant = "simulator" if "simulator" in identifier else None
                require(entry.get("SupportedPlatformVariant") == expected_variant, f"{name}: incorrect platform variant")
                packaged = output / identifier / entry["LibraryPath"]
                for resource in source.rglob("*"):
                    if resource.is_file() and resource != source / name:
                        require((packaged / resource.relative_to(source)).read_bytes() == resource.read_bytes(),
                                f"{name}: changed framework resource {resource.name}")
            device_output = output / "ios-arm64" / (name + ".framework") / name
            require(device_output.read_bytes() == arm64_device, f"{name}: device binary changed")
            simulator_output = output / "ios-arm64_x86_64-simulator" / (name + ".framework") / name
            for arch, expected in [("arm64", arm64_simulator), ("x86_64", x86_64_simulator)]:
                thin = module_work / (arch + "-check.bin")
                run("xcrun", "lipo", "-thin", arch, simulator_output, "-output", thin)
                require(thin.read_bytes() == expected, f"{name}: packaged {arch} binary changed")
            manifest[name] = {
                **metadata, "arm64_device_sha256": sha256(arm64_device),
                "x86_64_simulator_sha256": sha256(x86_64_simulator),
                "arm64_simulator_sha256": sha256(arm64_simulator),
                "arm64_object_count": count, "duplicate_object_names": duplicates,
            }
            print(f"Validated {name} {metadata['version']}: {count} objects, {duplicates} duplicate member names", flush=True)
        (staged / "conversion-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        publish(staged, root, [name + ".xcframework" for name in MODULES]
                + ["conversion-manifest.json"], backup)
    print(f"Installed validated XCFrameworks in {root}")


if __name__ == "__main__":
    main()
