require 'fastlane/action'
require_relative '../helper/git'
require_relative '../helper/changelog/document'
require_relative '../helper/changelog/writer'

module Fastlane
  module Actions
    class BuildChangelogAction < Action
      def self.run(params)
        version = params[:version]
        commits = params[:commits]
        features = commits.select(&:feat?)
        fixes = commits.select(&:fix?)
        changelog = Changelog::Document.new

        changelog.header(2) { link("https://github.com/#{Git.repo_name}/releases/tag/#{version}", version) }

        if features.any?
          changelog.header(3) { 'Features' }
          changelog.unordered_list { features.map(&:subject) }
        end

        if fixes.any?
          changelog.header(3) { 'Fixes' }
          changelog.unordered_list { fixes.map(&:subject) }
        end

        changelog
      end

      def self.description
        'Builds a changelog from conventional commits.'
      end

      def self.authors
        ['John Pignata', 'Ivan Artemiev']
      end

      def self.available_options
        [
          FastlaneCore::ConfigItem.new(
            key: :version,
            description: 'The version with which the changelog is associated',
            optional: false,
            type: String
          ),
          FastlaneCore::ConfigItem.new(
            key: :commits,
            description: 'The commits to use to build the changelog',
            optional: false,
            type: Commits
          )
        ]
      end

      def self.is_supported?(platform)
        true
      end
    end
  end
end
