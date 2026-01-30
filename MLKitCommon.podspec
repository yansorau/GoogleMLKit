# https://github.com/CocoaPods/Specs/blob/master/Specs/c/c/6/MLKitCommon/11.0.0/MLKitCommon.podspec.json
Pod::Spec.new do |s|
  s.name             = 'MLKitCommon'
  s.version          = '11.0.0'
  s.summary          = 'Fork of MLKitCommon with arm64 simulator binaries'
  s.homepage         = 'https://github.com/yansorau/GoogleMLKit'
  s.license          = { :type => 'Custom', :text => 'Google Intellectual Property' }
  s.author           = 'Google'
  s.source           = { :git => 'https://github.com/yansorau/GoogleMLKit.git', :branch => 'master' }
  s.platform         = :ios, '12.0'
  s.requires_arc     = true
  s.vendored_frameworks = 'MLKitCommon.xcframework'
  s.dependency 'GTMSessionFetcher/Core', '>= 3.3.2', '< 4.0'
  s.dependency 'GoogleDataTransport', '>= 9.4.1', '< 10.0'
  s.dependency 'GoogleToolboxForMac/Logger', '>= 4.2.1', '< 5.0'
  s.dependency 'GoogleToolboxForMac/NSData+zlib', '>= 4.2.1', '< 5.0'
  s.dependency 'GoogleUtilities/UserDefaults', '>= 7.13.0', '< 8.0'
  s.dependency 'GoogleUtilitiesComponents', '~> 1.0'
end