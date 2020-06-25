require 'strscan'
require_relative 'commit'

class Commit
  # Parser is a Conventional Commits 1.0.0 compliant parser that turns commit
  # messages into structured data. It uses StringScanner from the stdlib to
  # search through commit messages for tokens and extracts the type, scope,
  # subject, body, and footer from a commit message. If the parser finds a
  # commit that isn't written as a Conventional Commmit, it will default to
  # the type "change" and extract the subject and body.
  #
  # For more details on the specification, see
  # https://www.conventionalcommits.org/en/v1.0.0/#specification.
  class Parser
    # FOOTER_KEY is a pattern that matches a footer element of a Conventional
    # Commit. In the spec, commit messages can contain metadata in a footer that
    # are defined by a key and a value. The key is in one of three legal forms:
    #
    # - "key: "
    # - "key #"
    # - "BREAKING CHANGE: " (this pattern also supports "BREAKING CHANGES: ")
    FOOTER_KEY = /(^[\w-]+: |^[\w-]+ #|^BREAKING CHANGES?: )/

    attr_reader :commit

    def initialize(msg)
      @breaking_change = false
      @commit = Commit.new
      @msg = StringScanner.new(msg.strip)
    end

    def parse
      read_type_and_scope
      read_subject
      read_body
      read_footer

      return commit
    end

    private

    attr_reader :msg

    # Read the tokens that comprise the metadata prefixing the subject. [<type>[optional scope]: ]
    def read_type_and_scope
      commit.type = :change

      # Match the tokens that comprise the metadata prefixing the subject. This
      # must include a type such feat or fix, and can optionally include a scope
      # and a bang (!) to indicate a breaking change. Examples:
      #
      # - "fix: "
      # - "refactor(login-page): "
      # - "feat(core)!: "
      if msg.match?(/\w+(\([^\)]+\))?\!?: /)
        # Read up until a bang (!), colon (:), or open parenthesis (()
        commit.type = msg.scan(/[^!:\(]+/).downcase.to_sym

        case msg.getch
        when '('
          # Read up until a close parenthesis ())
          commit.scope = msg.scan(/[^\)]+/)
          msg.skip_until(/\): /)
        when '!'
          breaking_change!
          msg.skip_until(/: /)
        when ':'
          msg.getch
        end
      end
    end

    # Read the subject of the change. [<description>]
    def read_subject
      # Read an entire line up to a newline (\n)
      line = msg.scan(/[^\n]+/)
      commit.subject = line
      commit.breaking_change = line if breaking_change?
      msg.getch
    end

    # Read the body of the change. [[optional body]]
    def read_body
      commit.body = read_until_footer_key
    end

    def read_until_footer_key
      data = ''

      # Read until matching a new key or the end of the scanner. Valid footer keys
      # are at the beginning of a line.
      until (msg.match?(FOOTER_KEY) && msg.beginning_of_line?) || msg.eos?
        data << msg.getch
      end

      return data.strip
    end

    # Read any footers in the change [[optional footer(s)]]
    def read_footer
      return unless msg.check_until(FOOTER_KEY)

      while msg.rest?
        key = msg.scan_until(FOOTER_KEY)
        value = read_until_footer_key

        if key.match?(/BREAKING CHANGE/)
          breaking_change!
          commit.breaking_change = value
          commit.footer['BREAKING CHANGE'] = value
        elsif key.end_with?('#')
          commit.footer[key[0..-3]] = '#' + value
        else
          commit.footer[key[0..-3]] = value
        end
      end
    end

    def breaking_change?
      @breaking_change
    end

    def breaking_change!
      @breaking_change = true
    end
  end
end
