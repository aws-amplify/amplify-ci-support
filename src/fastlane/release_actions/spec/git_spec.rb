require 'spec_helper'
require 'helper/git'

describe Git do
  describe '.last_tag' do
    example do
      expect(Git).to receive(:run).and_return('1.0.2-13-gabcdef0123')
      expect(Git.last_tag).to eq('1.0.2')
    end

    examples do
      expect(Git).to receive(:run).and_return('v12.53.110-13-gabcdef0123')
      expect(Git.last_tag).to eq('v12.53.110')
    end
  end
end
