require 'fastlane_core/ui/ui'

class Git
  SEPARATOR = "=====END====="

  def self.last_version
    last_tag = run('git describe --tag', 'Could not find tag from HEAD')

    2.times { last_tag, = last_tag.rpartition('-') }
    last_tag
  end

  def self.log(from, to = 'HEAD')
    command = "git log --pretty='%s\n\n%b#{SEPARATOR}' #{from}..#{to}"
    log = run(command, 'Could not get log').strip

    log.split(SEPARATOR).map(&:strip)
  end

  # This is designed for usage with git SSH clone URLs as it strips
  # 'git@github.com:' from the front and '.git' from the end.
  def self.repo_name
    run('git remote get-url origin', 'Could not get origin url')[15..-6]
  end

  class << self
    def run(command, error)
      Fastlane::Action.sh(command, error_callback: -> { Fastlane::UI.crash!(error) })
    end
  end
end
