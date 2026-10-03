Pod::Spec.new do |s|
  s.name = 'MLKitNaturalLanguage'
  s.version = '10.0.0'
  s.summary = 'ML Kit Natural Language SDK with arm64 simulator support'
  s.homepage = 'https://github.com/TransGull/GoogleMLKit'
  s.author = 'Google, Inc.'
  s.license = { :type => 'Copyright', :text => 'Copyright 2025 Google LLC' }
  s.source = { :git => 'https://github.com/TransGull/GoogleMLKit.git', :branch => 'master' }
  s.ios.deployment_target = '15.5'
  s.vendored_frameworks = 'MLKitNaturalLanguage.xcframework'
  s.frameworks = ['Foundation']
  s.dependency 'GTMSessionFetcher/Core', '>= 3.3.2', '< 4.0'
  s.dependency 'GoogleToolboxForMac/Logger', '>= 4.2.1', '< 5.0'
  s.dependency 'GoogleToolboxForMac/NSData+zlib', '>= 4.2.1', '< 5.0'
  s.dependency 'GoogleToolboxForMac/StringEncoding', '>= 4.2.1', '< 5.0'
  s.dependency 'MLKitCommon', '~> 14.0'
end
