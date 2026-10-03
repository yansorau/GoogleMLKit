# Google ML Kit with Apple silicon simulator support

Local CocoaPods packaging of the official Google ML Kit SDKs. Minimum iOS version: **15.5**.

| Pod | Version | Official source |
| --- | --- | --- |
| MLKitLanguageID | 9.0.0 | [Google archive](https://dl.google.com/dl/cpdc/abd494a0381d8d03/MLKitLanguageID-9.0.0.tar.gz) |
| MLKitCommon | 14.0.0 | [Google archive](https://dl.google.com/dl/cpdc/00f258dabdb58dfa/MLKitCommon-14.0.0.tar.gz) |
| MLKitNaturalLanguage | 10.0.0 | [Google archive](https://dl.google.com/dl/cpdc/16c4bb76b6337f56/MLKitNaturalLanguage-10.0.0.tar.gz) |

Each XCFramework contains `ios-arm64` for devices and `ios-arm64_x86_64-simulator` for simulators. Headers, module maps, and privacy manifests come from the official archives. Dependency requirements match the corresponding [official CocoaPods Specs](https://github.com/CocoaPods/Specs).

## Local integration

With this repository beside your app repository:

```ruby
pod 'MLKitLanguageID', :path => '../GoogleMLKit'
pod 'MLKitCommon', :path => '../GoogleMLKit'
pod 'MLKitNaturalLanguage', :path => '../GoogleMLKit'
```

Versions are fixed by the local podspecs; CocoaPods does not allow a version requirement alongside an external `:path` source. The podspecs do not exclude arm64 simulators. Retain all three local declarations so transitive dependencies resolve to these converted binaries.

## Reproduce the conversion

Requires Python 3.9+ and Xcode command-line tools. Input must be the original official SDKs, organized as `SOURCE_ROOT/MLKitCommon/Frameworks/MLKitCommon.framework` and similarly for the other two SDKs. Download the linked archives and extract each into its own module directory.

```sh
# Use separately extracted official archives:
python3 scripts/convert_frameworks.py --source-root /path/to/official-sdks

# To validate new artifacts without replacing this repository's artifacts:
python3 scripts/convert_frameworks.py --source-root /path/to/official-sdks --output-root /path/to/staging
```

The script rejects inputs whose framework binary checksums differ from the pinned versions. It stages and validates all three XCFrameworks before replacing existing artifacts, and restores previous artifacts if publication fails.

For the simulator arm64 copy, it changes only `LC_BUILD_VERSION.platform` from `PLATFORM_IOS` (2) to `PLATFORM_IOSSIMULATOR` (7). Existing `minos` and `sdk` fields remain intact. Static archives are traversed by member byte offset: no objects are extracted or renamed, so duplicate member names, symbol indexes, padding, and relocations are preserved. Packaging uses `lipo` and `xcodebuild -create-xcframework`; original arm64 device and x86_64 simulator slices are preserved byte-for-byte.

Simulator conversion changes platform metadata rather than recompiling Google's source. Validate both simulator linking and actual language identification when changing SDK versions.

## Input binary SHA-256

These checksums refer to the original universal binary inside each official `.framework`, not the downloaded `.tar.gz`:

| Binary | SHA-256 |
| --- | --- |
| MLKitLanguageID | `4a05208e7881d3fcf0725ec8a3813b7a1a0afb5343e1089d2a118a343134c372` |
| MLKitCommon | `ee588e0b1bd6ca6f455001d59e769396ab40566acdd5001f85c54df24e487c54` |
| MLKitNaturalLanguage | `03677e13dd1071140cd24f1eebabd44df6a7ab2369aca62475780b27ac92e632` |

`conversion-manifest.json` also records device/simulator slice hashes, object counts, and duplicate member counts.
