class Version
  # Symbol holds details about the alphabet recognized by the Acceptor. It translates
  # characters into the an enumeration value for use in determining the right transition.
  module Symbol
    POSITIVE_INTEGER = 0
    ZERO = 1
    LETTER = 2
    DOT = 3
    DASH = 4
    PLUS = 5
    UNKNOWN = 99

    def self.for(character)
      case character
      when ('1'..'9')
        Symbol::POSITIVE_INTEGER
      when '0'
        Symbol::ZERO
      when ('A'..'Z'), ('a'..'z')
        Symbol::LETTER
      when '.'
        Symbol::DOT
      when '-'
        Symbol::DASH
      when '+'
        Symbol::PLUS
      else
        Symbol::UNKNOWN
      end
    end
  end

  # Acceptor is a deterministic finite automaton (DFA) that validates strings as
  # semantic versions. A DFA is a graph where the vertices are states (e.g. major,
  # minor, etc.) and the edges are transitions (e.g. start -> major). The DFA moves
  # between states using the transitions defined in the STATES constant as it processes
  # the characters of the input string. Certain states are designated as accepting,
  # meaning the state is a valid endpoint for the grammar being parsed. If the DFA
  # terminates in an accepting state, the string is valid and it accepts the
  # input. If the DFA cannot make a transition, finds an invalid character, or
  # terminates in a non-accepting state, the string is not valid. A simplified diagram
  # of the state machine can be found in this repo in
  # `docs/version-acceptor-dfa.{png,svg}` (drawn using http://madebyevan.com/fsm/).
  # While there's some complexity in maintaining the table of edges, it provides O(n)
  # runtime performance and has a maintainability edge over regular expressions.
  #
  # Acceptor is compliant with Semantic Versioning 2.0.0. For more details on the
  # specification, see: https://semver.org/.
  #
  # ==== Examples
  #
  #   Version::Acceptor.new('1.0.0').valid?            # => true
  #   Version::Acceptor.new('1.0.0-unstable.0').valid? # => true
  #   Version::Acceptor.new('1.0-alpha+234').valid?    # => true
  #   Version::Acceptor.new('1.0318.2').valid?         # => false
  #   Version::Acceptor.new('1.0.PRO).valid?           # => false
  #   Version::Acceptor.new('tetris').valid?           # => false
  class Acceptor
    ACCEPTING = [:patch, :patch_end, :prerelease, :build]

    START = :start

    STATES = {
      start: {
        Symbol::POSITIVE_INTEGER => :major,
        Symbol::ZERO => :major_end
      },

      major: {
        Symbol::POSITIVE_INTEGER => :major,
        Symbol::ZERO => :major,
        Symbol::DOT => :minor_start
      },

      major_end: {
        Symbol::DOT => :minor_start
      },

      minor_start: {
        Symbol::POSITIVE_INTEGER => :minor,
        Symbol::ZERO => :minor_end
      },

      minor: {
        Symbol::POSITIVE_INTEGER => :minor,
        Symbol::ZERO => :minor,
        Symbol::DOT => :patch_start
      },

      minor_end: {
        Symbol::DOT => :patch_start
      },

      patch_start: {
        Symbol::POSITIVE_INTEGER => :patch,
        Symbol::ZERO => :patch_end
      },

      patch: {
        Symbol::POSITIVE_INTEGER => :patch,
        Symbol::ZERO => :patch,
        Symbol::DASH => :prerelease,
        Symbol::PLUS => :build
      },

      patch_end: {
        Symbol::DASH => :prerelease,
        Symbol::PLUS => :build
      },

      prerelease: {
        Symbol::POSITIVE_INTEGER => :prerelease,
        Symbol::ZERO => :prerelease,
        Symbol::LETTER => :prerelease,
        Symbol::DASH => :prerelease,
        Symbol::DOT => :prerelease_new_identifier,
        Symbol::PLUS => :build
      },

      prerelease_new_identifier: {
        Symbol::POSITIVE_INTEGER => :prerelease,
        Symbol::ZERO => :prerelease,
        Symbol::LETTER => :prerelease,
        Symbol::DASH => :prerelease
      },

      build: {
        Symbol::POSITIVE_INTEGER => :build,
        Symbol::ZERO => :build,
        Symbol::LETTER => :build,
        Symbol::DASH => :build,
        Symbol::DOT => :build_new_identifier
      },

      build_new_identifier: {
        Symbol::POSITIVE_INTEGER => :build,
        Symbol::ZERO => :build,
        Symbol::LETTER => :build,
        Symbol::DASH => :build
      }
    }

    def initialize(candidate)
      unless candidate.respond_to?(:chars)
        raise ArgumentError, "Invalid argument: #{candidate}"
      end

      @candidate = candidate
    end

    def valid?
      state = START

      candidate.chars.each do |character|
        symbol = Symbol.for(character)

        if STATES[state].key?(symbol)
          state = STATES[state][symbol]
        else
          return false
        end
      end

      ACCEPTING.include?(state)
    end

    private

    attr_reader :candidate
  end
end
