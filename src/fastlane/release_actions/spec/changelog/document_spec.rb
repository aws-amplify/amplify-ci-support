require 'spec_helper'
require 'helper/changelog/document'

describe Changelog::Document do
  let(:document) { Changelog::Document.new }

  describe Changelog::Helper do
    let(:helper) { Changelog::Helper.new }

    describe "#link" do
      example { expect(helper.link('https://amazon.com', 'a bookstore')).to eq('[a bookstore](https://amazon.com)') }
    end

    describe "#bold" do
      example { expect(helper.bold('excelsior')).to eq('**excelsior**') }
    end

    describe "#em" do
      example { expect(helper.em('sotto voce')).to eq('*sotto voce*') }
    end
  end

  describe '#header' do
    example do
      document.header(1) do
        "Welcome To My Personal Web Page"
      end

      expect(document.render).to eq("# Welcome To My Personal Web Page\n\n")
    end

    example do
      document.header(5) do
        'I hear good things about ' + link('https://google.com', 'search engines')
      end

      expect(document.render).to eq("##### I hear good things about [search engines](https://google.com)\n\n")
    end
  end

  describe '#unordered_list' do
    example do
      document.unordered_list do
        ['Milk', 'Eggs', link('https://www.totinos.com', 'Pizza Rolls')]
      end

      expected = <<~TEXT.strip
      - Milk
      - Eggs
      - [Pizza Rolls](https://www.totinos.com)
      TEXT

      expect(document.render.strip).to eq(expected)
    end

    describe '#ordered_list' do
      example do
        document.ordered_list do
          ['Milk', 'Eggs', link('https://www.totinos.com', 'Pizza Rolls')]
        end

        expected = <<~TEXT.strip
        1. Milk
        2. Eggs
        3. [Pizza Rolls](https://www.totinos.com)
        TEXT

        expect(document.render.strip).to eq(expected)
      end
    end
  end
end
