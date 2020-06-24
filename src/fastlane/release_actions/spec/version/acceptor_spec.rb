require 'spec_helper'
require 'helper/version/acceptor'

describe Version::Acceptor do
  context 'when a string is not provided' do
    it 'raises ArgumentError' do
      expect { Version::Acceptor.new([]) }.to raise_error(ArgumentError)
    end
  end

  describe 'test table' do
    TABLE = [
      ['1.2.13', true],
      ['1.0.0', true],
      ['1.0.1', true],
      ['1.1.0', true],
      ['1.11.1', true],
      ['1.1.12', true],
      ['1.21.1', true],
      ['1.1.222', true],
      ['1.20.0', true],
      ['1.202.9', true],
      ['0.23.12', true],
      ['1.0.0-preview.0', true],
      ['1.0.0-abcdefg123456.thingandother.thing+8675309', true],
      ['99.3.2', true],
      ['0.0.0', true],
      ['0.0.1', true],
      ['0.1.1', true],
      ['1.0.0+123', true],
      ['1.0.0-alpha.1+123', true],
      ['0', false],
      ['0.0', false],
      ['1+123', false],
      ['1.0+123', false],
      ['', false, 'an empty string'],
      ['tetris', false, 'a word'],
      ['1.0.0.0', false],
      ['0.0.0.0', false],
      ['1.0.%', false],
      ['1.0.0p', false],
      ['1.0318.2', false]
    ]

    # Instead of writing individual expectations, this method generates tests dynamically from
    # a table. The table includes an input string, an expected validity result, and an optional
    # label for specdoc output.
    #
    # This method is popular in the Go community, and is applicable here given the number of
    # combinations to test. To learn more, see: https://dave.cheney.net/2019/05/07/prefer-table-driven-tests
    TABLE.each do |candidate, valid, display|
      context(display || candidate) do
        example do
          acceptor = Version::Acceptor.new(candidate)

          if valid
            expect(acceptor).to be_valid
          else
            expect(acceptor).not_to be_valid
          end
        end
      end
    end
  end
end
