class Commits
  include Enumerable

  def self.from(messages)
    commits = messages.map { |message| Commit::Parser.new(message).parse }

    new(commits)
  end

  def initialize(commits = [])
    @commits = commits
  end

  def each(&block)
    commits.each(&block)
  end

  def push(commit)
    commits.push(commit)
  end

  alias << push

  def breaking_change?
    commits.any?(&:breaking_change?)
  end

  def feat?
    commits.any? { |commit| commit.type == :feat }
  end

  def fix?
    commits.any? { |commit| commit.type == :fix }
  end

  def empty?
    commits.empty?
  end

  private

  attr_reader :commits
end
