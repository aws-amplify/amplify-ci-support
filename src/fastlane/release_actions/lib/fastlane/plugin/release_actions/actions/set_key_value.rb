module Fastlane
  module Actions
    class SetKeyValueAction < Action
      def self.run(params)
        file = params[:file]
        key = params[:key]
        value = params[:value]

        regex_key = /(?<=#{key})(\s*=\s*["'].*)/
        file_contents = File.read(file)

        unless file_contents.match(regex_key)
          UI.error("#{key} not present or doesn't have an explicit value in #{file}")
          return
        end

        new_value = " = '#{value}'"

        file_contents = file_contents.gsub(regex_key, new_value)

        File.open(file, "w") { |f| f.puts(file_contents) }
        UI.success("Successfully modified #{key} to value #{value} in #{file}")
      end

      def self.description
        'This action will modify the value of the passed in key'
      end

      def self.available_options
        [
          FastlaneCore::ConfigItem.new(
            key: :file,
            env_name: 'FILE_PATH',
            description: 'The path of the file you wish to modify',
            optional: false,
            type: String
          ),
          FastlaneCore::ConfigItem.new(
            key: :key,
            env_name: 'KEY_NAME',
            description: 'The key of the value you wish to modify',
            optional: false,
            type: String
          ),
          FastlaneCore::ConfigItem.new(
            key: :value,
            env_name: 'KEY_VALUE',
            description: 'The new value to assign to the key',
            optional: false,
            type: String
          )
        ]
      end

      def self.authors
        ['John Pignata', 'Ivan Artemiev']
      end

      def self.is_supported?(platform)
        true
      end
    end
  end
end
