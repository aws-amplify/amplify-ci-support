module Changelog
  # Helper is an object holding convenience methods for usage in blocks passed
  # to the node builds to decorate pieces of text with Markdown syntax.
  class Helper
    def link(url, label)
      "[#{label}](#{url})"
    end

    def bold(text)
      "**#{text}**"
    end

    def em(text)
      "*#{text}*"
    end
  end

  # Document provides a simple Domain Specific Language (DSL) for creating
  # Markdown documents. It's fairly limited and meant to just support the subset
  # required to maintain CHANGELOG.md files. Each element takes a block which
  # holds some content to render as that element. Blocks passed to each method
  # is evaluated in the context of a Changelog::Helper instance allowing the use
  # of #link, #bold, #em.
  #
  # ==== Examples
  #
  #   document = Document.new
  #   document.header(1) { 'CHANGELOG' }
  #   document.header(2) { link('https://github.com/jpignata/myrepo', '1.0.0') }
  #   document.header(3) { 'Features' }
  #   document.ordered_list { [bold('Initial release'), 'Login page', 'Logout page'] }
  #
  #   document.render # => <<-EOF
  #   # CHANGELOG
  #
  #   ## [1.0.0](https://github.com/pignata/myrepo)
  #
  #   ### Features
  #
  #   - **Initial release**
  #   - Login page
  #   - Logout page
  #   EOF
  class Document
    attr_reader :nodes

    def initialize
      @nodes = []
      @helper = Helper.new
    end

    def render
      nodes.join
    end

    def header(level, &block)
      nodes << concat('#' * level + ' ', helper.instance_eval(&block), "\n")
      line_break
    end

    def ordered_list(&block)
      helper.instance_eval(&block).each.with_index do |item, i|
        nodes << concat("#{i + 1}. ", item, "\n")
      end

      line_break
    end

    def unordered_list(&block)
      helper.instance_eval(&block).each do |item|
        nodes << concat('- ', item, "\n")
      end

      line_break
    end

    def line_break
      nodes << "\n"
    end

    private

    attr_reader :helper

    def concat(*items)
      items.join
    end
  end
end
