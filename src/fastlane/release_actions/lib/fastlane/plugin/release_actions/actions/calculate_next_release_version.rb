require 'fastlane/action'
require_relative '../helper/commit/commit'
require_relative '../helper/commit/commits'
require_relative '../helper/commit/footer'
require_relative '../helper/commit/parser'
require_relative '../helper/git'

module Fastlane
  module Actions
    class CalculateNextReleaseVersionAction < Action
      def self.run(params)
        release_tag_prefix = params[:release_tag_prefix]
        last_tag = params[:from_tag].nil? ? Git.last_release_tag : params[:from_tag]
        version = Version.from(last_tag, release_tag_prefix)
        messages = Git.log(last_tag)
        commits = Commits.from(messages)

        if commits.empty?
          UI.crash!('No commits found since last release')
        end

        [bump_version(version, commits).to_s, commits]
      end

      def self.bump_version(version, commits)
        if commits.breaking_change?
          version.bump_major
        elsif commits.feat?
          version.bump_minor
        else
          version.bump_patch
        end
      end

      def self.return_value
        'An array containing the next version calculated from the previous tag, and the commits used to calculate that version.'
      end

      def self.description
        'Actions to use your commit history to tag, generate changelogs, and push a release.'
      end

      def self.authors
        ['John Pignata', 'Ivan Artemiev']
      end

      def self.available_options
        [
          FastlaneCore::ConfigItem.new(key: :release_tag_prefix,
            description: "Release tag prefix. Default = v",
            default_value: 'v'),
          FastlaneCore::ConfigItem.new(
            key: :from_tag,
            env_name: 'FROM_TAG',
            description: 'Use this tag value as the last release',
            type: String,
            optional: true,
            default_value: nil
          )
        ]
      end

      def self.is_supported?(platform)
        true
      end
    end
  end
end
