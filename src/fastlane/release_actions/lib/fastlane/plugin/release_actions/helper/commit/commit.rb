require_relative 'footer'

class Commit
  attr_accessor :type, :scope, :breaking_change, :subject, :body
  attr_reader :footer

  def initialize
    @footer = Footer.new
  end

  def breaking_change?
    !breaking_change.nil?
  end

  def feat?
    type == :feat
  end

  def fix?
    type == :fix
  end

  def inspect
    "#<Commit type:, #{type}, subject: #{subject}>"
  end

  alias to_s inspect
end
