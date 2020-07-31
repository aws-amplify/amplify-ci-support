require 'fastlane_core/ui/ui'

class Git
  SEPARATOR = "=====END====="

  def self.last_tag(tag_type = 'lightweight')
    if tag_type == 'lightweight'
      command = %w(git describe --tag --long)
      tag = run(command, 'Could not find tag from HEAD')

      2.times { tag, = tag.rpartition('-') }
    else
      command = %w(git tag --sort='-creatordate' | head -n 1)
      tag = run(command, 'Could not find tag from HEAD').strip!
    end
    tag
  end

  def self.last_release_tag
    command = 'git tag | sort -r | grep -v unstable | head -1'
    run(command, 'Could not list tags').chomp
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
