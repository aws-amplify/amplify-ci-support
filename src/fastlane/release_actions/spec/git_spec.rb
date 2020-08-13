require 'spec_helper'
require 'helper/git'

describe Git do
  describe '.last_tag' do
    example do
      expect(Git).to receive(:run).and_return('1.0.2-13-gabcdef0123')
      expect(Git.last_tag).to eq('1.0.2')
    end

    example do
      expect(Git).to receive(:run).and_return('v12.53.110-13-gabcdef0123')
      expect(Git.last_tag).to eq('v12.53.110')
    end
  end

  describe '.last_release_tag' do
    example do
      expect(Git).to receive(:run).and_return("v1.0.5-alpha.1 v1.0.5-alpha.0 v1.0.4 v1.0.3 v0.10.0 v0.0.1 v0.0.1-preview.0")
      expect(Git.last_release_tag).to eq('v1.0.4')
    end

    example do
      expect(Git).to receive(:run).and_return("v1.10.0 v1.8.0")
      expect(Git.last_release_tag).to eq('v1.10.0')
    end

    example do
      expect(Git).to receive(:run).and_return("v1.10.0-dev.0\nv1.10.0\nv1.8.0\n\n")
      expect(Git.last_release_tag).to eq('v1.10.0')
    end
  end
end
