require 'date'
require 'fastlane/action'
require_relative '../helper/git'
require_relative '../helper/changelog/document'

module Fastlane
  module Actions
    class BuildChangelogAction < Action
      def self.run(params)
        version = params[:version]
        commits = params[:commits]
        features = commits.select(&:feat?)
        fixes = commits.select(&:fix?)
        breaking_changes = commits.select(&:breaking_change?)
        changelog = Changelog::Document.new

        changelog.header(2) { "#{version} (#{Date.today})" }

        if breaking_changes.any?
          changelog.header(3) { '⚠️ BREAKING CHANGES' }
          changelog.unordered_list { breaking_changes.map(&:breaking_change) }
        end

        if features.any?
          changelog.header(3) { 'Features' }
          changelog.unordered_list do
            features.map do |change|
              change.scope ? "#{bold(change.scope)}: #{change.subject}" : change.subject
            end
          end
        end

        if fixes.any?
          changelog.header(3) { 'Bug Fixes' }
          changelog.unordered_list do
            fixes.map do |change|
              change.scope ? "#{bold(change.scope)}: #{change.subject}" : change.subject
            end
          end
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
