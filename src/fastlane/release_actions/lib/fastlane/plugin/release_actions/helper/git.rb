require 'fastlane_core/ui/ui'

class Git
  SEPARATOR = "=====END====="

  def self.last_tag
    command = %w(git describe --tag --long)
    tag = run(command, 'Could not find tag from HEAD')

    2.times { tag, = tag.rpartition('-') }

    tag
  end

  # Return the next release tag after looking at the list of tags below the parameter below
  def self.last_release_tag(below = "v100.0.0")
    command = %w(git tag)
    tags = run(command, 'Could not list tags').chomp.gsub(/\s+/m, ' ').strip.split
    release_tags = tags.reject { |tag| Version.from(tag).prerelease? }
    tag_limit = Version.from(below)
    filtered_tags = release_tags.reject { |tag| Version.from(tag) >= tag_limit }
    filtered_tags.max_by { |tag| Version.from(tag) }
  end

  def self.log(from, to = 'HEAD')
    command = %W(git log --pretty='%s\n\n%b#{SEPARATOR}' #{from}..#{to})
    log = run(command, 'Could not get log').strip

    log.split(SEPARATOR).map(&:strip)
  end

  # This is designed for usage with git SSH clone URLs as it strips
  # 'git@github.com:' from the front and '.git' from the end.
  def self.repo_name
    command = %w(git remote get-url origin)
    run(command, 'Could not get origin url')[15..-6]
  end

  class << self
    def run(command, error)
      Fastlane::Action.sh(command, error_callback: -> { Fastlane::UI.crash!(error) })
    end
  end
end
