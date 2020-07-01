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
        tag = Git.last_release_tag
        version = Version.from(tag)
        messages = Git.log(tag)
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
        []
      end

      def self.is_supported?(platform)
        true
      end
    end
  end
end
