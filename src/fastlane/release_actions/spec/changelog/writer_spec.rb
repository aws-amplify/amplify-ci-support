require 'spec_helper'
require 'tempfile'
require 'helper/changelog/writer'
require 'helper/changelog/document'

describe Changelog::Writer do
  let(:file) { Tempfile.new('CHANGELOG') }

  let(:document) do
    Changelog::Document.new.tap do |document|
      document.header(2) { '1.0.1' }
      document.header(3) { 'Fixes' }
      document.unordered_list do
        [
          'Oops, that did not work',
          'Yeah, uh, that did not work either'
        ]
      end
    end
  end

  before do
    file.write(<<~TEXT)
    # Changelog

    ## 1.0.0

    ### Features

    - Initial release
    TEXT

    file.close
  end

  example do
    writer = Changelog::Writer.new(document, file)
    writer.write
    file.open

    expected = <<~TEXT
    # Changelog

    ## 1.0.1

    ### Fixes

    - Oops, that did not work
    - Yeah, uh, that did not work either

    ## 1.0.0

    ### Features

    - Initial release
    TEXT
    expect(file.read).to eq(expected)
  end
end
