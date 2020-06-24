require 'spec_helper'
require 'helper/commit/footer'

describe Commit::Footer do
  let(:footer) { Commit::Footer.new }

  it 'is enumerable' do
    footer['key1'] = 1
    footer['key2'] = 2

    expect(footer.each.to_a).to eq([['key1', 1], ['key2', 2]])
  end

  describe 'key access' do
    KEY = 'key'

    # A quick way to generate all permutations of casing for a given string. The
    # number of permutations is 2**N where N is the length of the subject. This
    # iterates the number of permutations times, turning a character uppercase if the
    # inner iteration number bit is set in the outer iteration number.
    #
    # For example, for a string of length 3 ("key"), on the first iteration (0, (0, 1, 2)),
    # no bits are set so a lowercase string is returned ("key"). On the second outer
    # iteration (1, (0, 1, 2)), the 1 bit is set, so the first character is returned
    # uppercase. ("Key") On the six iteration (5, (0, 1, 2)), the 1 and 4 bits are
    # set, so the first and last characters are returned uppercase ("KeY").
    #
    # Given the KEY "key", this results in:
    # - "key"
    # - "Key"
    # - "kEy"
    # - "KEy"
    # - "keY
    # - "KeY"
    # - "kEY"
    # - "KEY"
    #
    # This is likely overkill for this test, but I wrote it, so here it is. This method
    # generates expectations for each permutation.
    KEYS = Array.new(1 << KEY.length) do |i|
      chars = KEY.each_char.map.with_index do |char, j|
        if i & (1 << j) > 0
          char.upcase
        else
          char
        end
      end

      chars.join
    end

    it 'is case insensitive' do
      footer[KEY] = 'value'

      KEYS.each do |key|
        expect(footer[key]).to eq('value')
      end
    end
  end
end
