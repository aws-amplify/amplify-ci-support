require 'spec_helper'
require 'helper/git'

describe Git do
  describe '.last_version' do
    example do
      expect(Git).to receive(:run).and_return('1.0.2-13-gabcdef0123')
      expect(Git.last_version).to eq('1.0.2')
    end

    context 'the tag is prepended with a "v"' do
      it 'removes the "v"' do
        expect(Git).to receive(:run).and_return('v1.0.2-13-gabcdef0123')
        expect(Git.last_version).to eq('1.0.2')
      end
    end
  end
end
