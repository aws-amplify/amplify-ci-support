require_relative 'acceptor'

# Version represents a semantic version as defined by Semantic Versioning 2.0.0.
# Semantic versions must include a normal version number (i.e. 1.0.0) and can
# optionally include labels indicating pre-release version and/or build metadata.
# Version can compare and bump segments of a semantic version.
#
# For more details on the specification, see: https://semver.org/.
class Version
  include Comparable

  attr_reader :segments, :prerelease, :build

  def initialize(version)
    # Acceptor ensures our input version is valid per the semver spec. See
    # `Version::Acceptor` for details.
    unless Acceptor.new(version).valid?
      raise ArgumentError, "Invalid version: #{version}"
    end

    parts = version.split(/[-\+]/)

    @segments = parts[0].split('.').map(&:to_i)
    @prerelease = parts[1] if version.include?('-')
    @build = parts[-1] if version.include?('+')
  end

  # bump_major increments the major version. (e.g. 1.0.0 -> 2.0.0)
  def bump_major!
    bump(0)
  end

  # bump_minor increments the minor version. (e.g. 1.0.0 -> 1.1.0)
  def bump_minor!
    bump(1)
  end

  # bump_patch increments the patch version. (e.g. 1.0.0 -> 1.0.1)
  def bump_patch!
    bump(2)
  end

  # bump_prerelease increments the prerelease version. (e.g. 1.0.0-alpha.0 -> 1.0.0-alpha.1)
  # There's no specification for how prerelease tokens are structured beyond dot-separated
  # identifiers that might be numeric and might not be. The approach taken here is to siphon
  # off any digit characters at the end of the token, increment it as an integer, and
  # reassemble the string. Calling this without a prerelease set or with a token without
  # trailing digits (e.g. -alpha.beta) will raise an `ArgumentError`.
  def bump_prerelease!
    if !prerelease?
      raise ArgumentError, 'No prerelease present to bump'
    elsif !prerelease[-1].between?("0", "9")
      raise ArgumentError, 'prerelease does not end with an integer'
    end

    integer = @prerelease.slice(/\d+$/)
    next_prerelease = @prerelease.delete_suffix(integer) + integer.next

    new(segments, next_prerelease)
  end

  def prerelease!(token)
    new(segments, token + '.0')
  end

  def prerelease?
    !prerelease.nil?
  end

  def to_s
    version
  end

  def inspect
    "#<Version: '#{version}'>"
  end

  def ==(other)
    version == other.version
  end

  def <=>(other)
    if segments != other.segments
      return segments <=> other.segments
    end

    if prerelease.nil? && other.prerelease.nil?
      return 0
    elsif prerelease.nil? && !other.prerelease.nil?
      return 1
    elsif !prerelease.nil? && other.prerelease.nil?
      return -1
    end

    mine = prerelease.split('.')
    theirs = other.prerelease.split('.')

    [prerelease, other.prerelease].map(&:size).max.times do |i|
      next if mine[i] == theirs[i]

      if mine[i].nil?
        return -1
      elsif theirs[i].nil?
        return 1
      elsif numeric?(mine[i]) && numeric?(theirs[i])
        return mine[i].to_i <=> theirs[i].to_i
      else
        return mine[i] <=> theirs[i]
      end
    end

    return 0
  end

  protected

  # These writers allow an instance to create a new instance with different data.
  # This pattern is used to ensure objects themselves are immutable but return new
  # instances when a mutation is made (e.g. bump_*).
  attr_writer :segments, :prerelease, :build

  # protected methods in ruby are only callable by the object itself, and objects
  # of the same class. This is only used by the equality and comparison operators
  # and thus is marked protected.
  def version
    version = segments.join('.')
    version = [version, prerelease].compact.join('-')

    [version, build].compact.join('+')
  end

  private

  # bump is used by the public methods to increment a specific segment of the normal
  # version. It expects to be called with 0, 1, or 2 relating to the major, minor, and
  # patch segments respectively. Prerelease and build metadata is not retained.
  def bump(segment)
    next_segments = segments.dup.tap do |segments|
      segments[segment] += 1
    end

    return new(next_segments)
  end

  # This is a private construction method called in the bump methods. Object#allocate
  # creates a new instance without running the initializer which allows an instance to
  # assemble another instance with derived data without processing a version string. THis
  # method doesn't pass along build information as builds are only germaine to a single
  # instance of a Version and not incrementable or transferrable.
  def new(segments, prerelease = nil)
    self.class.allocate.tap do |version|
      version.segments = segments
      version.prerelease = prerelease
    end
  end

  def numeric?(character)
    true if Float(character)
  rescue ArgumentError, TypeError
    false
  end
end
