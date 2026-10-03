Pod::Spec.new do |s|
  s.name = 'MLKitLanguageID'
  s.version = '9.0.0'
  s.summary = 'ML Kit Language Identification SDK with arm64 simulator support'
  s.homepage = 'https://github.com/TransGull/GoogleMLKit'
  s.author = 'Google, Inc.'
  s.license = { :type => 'Copyright', :text => 'Copyright 2025 Google LLC' }
  s.source = { :git => 'https://github.com/TransGull/GoogleMLKit.git', :branch => 'master' }
  s.ios.deployment_target = '15.5'
  s.module_name = 'MLKitLanguageID'
  s.vendored_frameworks = 'MLKitLanguageID.xcframework'
  s.frameworks = ['Foundation']
  s.libraries = ['c++']
  s.dependency 'MLKitNaturalLanguage', '~> 10.0'
end
