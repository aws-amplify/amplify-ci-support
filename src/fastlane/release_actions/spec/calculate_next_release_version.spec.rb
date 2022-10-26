require 'spec_helper'
require 'actions/calculate_next_release_version'

describe Fastlane do
  describe Fastlane::FastFile do
    describe "calculate_next_release_version" do
      example do
        expect(Git).to receive(:run).and_return("v1.10.0 v1.8.0")
        expect(Git).to receive(:log).and_return(["chore: some chore", "feat: some feat"])
        result = Fastlane::FastFile.new.parse("
          lane :test do
            calculate_next_release_version
          end
        ").runner.execute(:test)
        expect(result[0]).to eq('1.11.0')
      end

      example do
        expect(Git).to receive(:run).and_return("v1.10.0 v1.8.0 v2.1.2")
        expect(Git).to receive(:log).and_return(["chore: some chore"])
        result = Fastlane::FastFile.new.parse("
          lane :test do
            calculate_next_release_version(version_limit:'v2.0.0')
          end
        ").runner.execute(:test)
        expect(result[0]).to eq('1.10.1')
      end
    end
  end
end
