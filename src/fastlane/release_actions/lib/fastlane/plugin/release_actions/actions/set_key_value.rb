require_relative '../helper/key_value'

module Fastlane
  module Actions
    class SetKeyValueAction < Action
      def self.run(params)
        key = params[:key]
        file = params[:file]
        value = params[:value]

        key_value = KeyValue.new(key)

        begin
          key_value.match_and_replace_file(file: file, value: value)
        rescue => exception
          UI.error(exception)
          raise exception
        end

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
