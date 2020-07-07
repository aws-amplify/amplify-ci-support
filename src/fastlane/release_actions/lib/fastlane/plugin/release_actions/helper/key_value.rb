class KeyValue
  def initialize(key)
    # Will match just the value that's contained inside of either single or double quotes
    # E.g., if key = AMPLIFY_VERSION and the file contains: $AMPLIFY_VERSION = "1.3.3"
    # it will match 1.3.3
    @regex_key = /(#{key}\s*=\s*["']\K)([\d\w.-]?)*/
  end

  def match_and_replace_file(file:, value:)
    file_contents = File.read(file)

    unless match(file_contents)
      raise StandardError, "#{key} not present or doesn't have an explicit value in #{file}"
    end

    file_contents = replace(file_contents: file_contents, value: value)
    File.open(file, "w") { |f| f.puts(file_contents) }
  end

  def match(file_contents)
    file_contents.match(@regex_key)
  end

  def replace(file_contents:, value:)
    file_contents.gsub(@regex_key, value)
  end
end
