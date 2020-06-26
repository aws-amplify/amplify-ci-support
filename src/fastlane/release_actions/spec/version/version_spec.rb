require 'spec_helper'
require 'helper/version/version'

describe Version do
  it 'is instantiated with a version string' do
    expect(Version.new('1.0.0').segments).to eq([1, 0, 0])
  end

  context 'with an invalid version string' do
    it 'raises an exception' do
      expect { Version.new('potatoes') }.to raise_error(ArgumentError)
      expect { Version.new('3.51.0.1057') }.to raise_error(ArgumentError)
    end
  end

  describe '#bump_major' do
    context Version.new('1.0.0') do
      example { expect(subject.bump_major).to eq(Version.new('2.0.0')) }
    end

    context Version.new('2.1.15') do
      example { expect(subject.bump_major).to eq(Version.new('3.0.0')) }
    end
  end

  describe '#bump_minor' do
    context Version.new('1.0.0') do
      example { expect(subject.bump_minor).to eq(Version.new('1.1.0')) }
    end

    context Version.new('2.1.15') do
      example { expect(subject.bump_minor).to eq(Version.new('2.2.0')) }
    end
  end

  describe '#bump_patch' do
    context Version.new('1.0.0') do
      example { expect(subject.bump_patch).to eq(Version.new('1.0.1')) }
    end

    context Version.new('2.1.15') do
      example { expect(subject.bump_patch).to eq(Version.new('2.1.16')) }
    end
  end

  describe '#bump_prelease' do
    context '1.0.0-alpha.0' do
      let(:version) { Version.new('1.0.0-alpha.0') }
      example { expect(version.bump_prerelease).to eq(Version.new('1.0.0-alpha.1')) }
    end

    context '1.0.0' do
      let(:version) { Version.new('1.0.0') }
      example { expect { version.bump_prerelease }.to raise_error(ArgumentError) }
    end

    context '1.0.0-alpha' do
      let(:version) { Version.new('1.0.0-alpha') }
      example { expect { version.bump_prerelease }.to raise_error(ArgumentError) }
    end
  end

  describe '#as_prerelease' do
    it 'adds a given token as the first prerelease of the version' do
      version = Version.new('1.0.0')
      expect { version.as_prerelease('alpha').to eq(Version.new('1.0.0-alpha.0')) }
    end
  end

  describe 'Comparable' do
    it 'sorts based upon semver' do
      preview = Version.new('0.10.0')
      one_dot_oh = Version.new('1.0.0')
      two_dot_oh = Version.new('2.0.0')

      expect([two_dot_oh, preview, one_dot_oh].sort).to eq([preview, one_dot_oh, two_dot_oh])
      expect(one_dot_oh).to be > preview
      expect(two_dot_oh).to be > one_dot_oh
    end

    it 'does not change the order of equal objects' do
      first = Version.new('1.0.0')
      second = Version.new('1.0.0')
      third = Version.new('1.0.0')
      sorted = [first, second, third].sort
      hashes = sorted.map(&:hash)

      expect(hashes).to eq([first.hash, second.hash, third.hash])
    end

    example 'prerelease versions have a lower precendence' do
      one_dot_oh = Version.new('1.0.0')
      rc = Version.new('1.0.0-rc')

      expect(one_dot_oh).to be > rc
    end

    example 'versions are compared according to the spec rules' do
      # This is the test case outlined in https://semver.org/#spec-item-11.

      expect(Version.new('1.0.0')).to be > Version.new('1.0.0-rc.1')
      expect(Version.new('1.0.0-rc.1')).to be > Version.new('1.0.0-beta.11')
      expect(Version.new('1.0.0-beta.11')).to be > Version.new('1.0.0-beta.2')
      expect(Version.new('1.0.0-beta.2')).to be > Version.new('1.0.0-beta')
      expect(Version.new('1.0.0-beta')).to be > Version.new('1.0.0-alpha.beta')
      expect(Version.new('1.0.0-alpha.beta')).to be > Version.new('1.0.0-alpha.1')
      expect(Version.new('1.0.0-alpha.1')).to be > Version.new('1.0.0-alpha')
    end
  end
end
