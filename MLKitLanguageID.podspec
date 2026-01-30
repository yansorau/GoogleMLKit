# https://github.com/CocoaPods/Specs/blob/master/Specs/f/8/1/MLKitLanguageID/6.0.0/MLKitLanguageID.podspec.json
Pod::Spec.new do |s|
  s.name             = 'MLKitLanguageID'
  s.version          = '6.0.0'
  s.summary          = 'Fork of MLKitLanguageID with arm64 simulator binaries'
  s.homepage         = 'https://github.com/yansorau/GoogleMLKit'
  s.license          = { :type => 'Custom', :text => 'Google Intellectual Property' }
  s.author           = 'Google'
  s.source           = { :git => 'https://github.com/yansorau/GoogleMLKit.git', :branch => 'master' }
  s.platform         = :ios, '12.0'
  s.requires_arc     = true
  s.vendored_frameworks = 'MLKitLanguageID.xcframework'
  s.dependency 'MLKitNaturalLanguage', '~> 7.0'
end