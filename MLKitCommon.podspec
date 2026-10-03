Pod::Spec.new do |s|
  s.name = 'MLKitCommon'
  s.version = '14.0.0'
  s.summary = 'ML Kit Common SDK with arm64 simulator support'
  s.homepage = 'https://github.com/TransGull/GoogleMLKit'
  s.author = 'Google, Inc.'
  s.license = { :type => 'Copyright', :text => 'Copyright 2025 Google LLC' }
  s.source = { :git => 'https://github.com/TransGull/GoogleMLKit.git', :branch => 'master' }
  s.ios.deployment_target = '15.5'
  s.module_name = 'MLKitCommon'
  s.vendored_frameworks = 'MLKitCommon.xcframework'
  s.frameworks = ['Foundation', 'LocalAuthentication']
  s.libraries = ['c++', 'sqlite3', 'z']
  s.dependency 'GTMSessionFetcher/Core', '>= 3.3.2', '< 4.0'
  s.dependency 'GoogleDataTransport', '~> 10.0'
  s.dependency 'GoogleToolboxForMac/Logger', '>= 4.2.1', '< 5.0'
  s.dependency 'GoogleToolboxForMac/NSData+zlib', '>= 4.2.1', '< 5.0'
  s.dependency 'GoogleUtilities/Logger', '~> 8.0'
  s.dependency 'GoogleUtilities/UserDefaults', '~> 8.0'
end
