require 'spec_helper'
require 'actions/calculate_next_canary_version'

describe Fastlane do
  describe Fastlane::FastFile do
    describe "calculate_next_canary_version" do
      example do
        expect(Git).to receive(:last_tag).and_return('v1.0.2')
        result = Fastlane::FastFile.new.parse("
          lane :test do
            calculate_next_canary_version
          end
        ").runner.execute(:test)
        expect(result).to eq('1.0.3-unstable.0')
      end

      example do
        expect(Git).to receive(:last_tag).and_return('v1.0.2')
        result = Fastlane::FastFile.new.parse("
          lane :test do
            calculate_next_canary_version(prerelease_identifier: 'dev')
          end
        ").runner.execute(:test)
        expect(result).to eq('1.0.3-dev.0')
      end

      example do
        expect(Git).to receive(:last_tag).and_return('v1.0.3-dev.3')
        result = Fastlane::FastFile.new.parse("
          lane :test do
            calculate_next_canary_version
          end
        ").runner.execute(:test)
        expect(result).to eq('1.0.3-dev.4')
      end

      example do
        expect(Git).to receive(:last_tag).and_return('v1.0.3-dev.3')
        result = Fastlane::FastFile.new.parse("
          lane :test do
            calculate_next_canary_version(prerelease_identifier: 'anything')
          end
        ").runner.execute(:test)
        expect(result).to eq('1.0.3-dev.4')
      end
    end
  end
end
