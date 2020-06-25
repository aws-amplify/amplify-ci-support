require 'fastlane/action'

module Fastlane
  module Actions
    class WriteChangelogAction < Action
      def self.run(params)
        changelog = params[:changelog]
        path = params[:path]

        Changelog::Writer.new(changelog, path).write
      end

      def self.description
        'Adds the latest release to the changelog.'
      end

      def self.authors
        ['John Pignata', 'Ivan Artemiev']
      end

      def self.available_options
        [
          FastlaneCore::ConfigItem.new(
            key: :changelog,
            description: 'The changelog document to write',
            optional: false,
            type: Changelog::Document
          ),
          FastlaneCore::ConfigItem.new(
            key: :path,
            description: 'Path to the changelog file for the project',
            optional: false,
            type: String
          )
        ]
      end

      def self.is_supported?(platform)
        true
      end
    end
  end
end
