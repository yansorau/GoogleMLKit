# https://github.com/CocoaPods/Specs/blob/master/Specs/0/d/7/MLKitNaturalLanguage/7.0.0/MLKitNaturalLanguage.podspec.json
Pod::Spec.new do |s|
  s.name             = 'MLKitNaturalLanguage'
  s.version          = '7.0.0'
  s.summary          = 'Fork of MLKitNaturalLanguage with arm64 simulator binaries'
  s.homepage         = 'https://github.com/yansorau/GoogleMLKit'
  s.license          = { :type => 'Custom', :text => 'Google Intellectual Property' }
  s.author           = 'Google'
  s.source           = { :git => 'https://github.com/yansorau/GoogleMLKit.git', :branch => 'master' }
  s.platform         = :ios, '12.0'
  s.requires_arc     = true
  s.vendored_frameworks = 'MLKitNaturalLanguage.xcframework'
  s.dependency 'GTMSessionFetcher/Core', '>= 3.3.2', '< 4.0'
  s.dependency 'GoogleToolboxForMac/Logger', '>= 4.2.1', '< 5.0'
  s.dependency 'GoogleToolboxForMac/NSData+zlib', '>= 4.2.1', '< 5.0'
  s.dependency 'GoogleToolboxForMac/StringEncoding', '>= 4.2.1', '< 5.0'
  s.dependency 'MLKitCommon', '~> 11.0'
end