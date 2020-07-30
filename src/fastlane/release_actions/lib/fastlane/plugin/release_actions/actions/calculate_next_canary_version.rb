require 'fastlane/action'
require_relative '../helper/git'
require_relative '../helper/version/version'

module Fastlane
  module Actions
    class CalculateNextCanaryVersionAction < Action
      def self.run(params)
        last_tag = Git.last_tag(params[:release_tag_type])
        version = Version.from(last_tag, params[:release_tag_prefix])
        if version.prerelease?
          version = version.bump_prerelease
        else
          version = version.bump_patch
          version = version.as_prerelease('unstable')
        end
        # Returning the version object instead of just the string.
        return version
      end

      def self.description
        'Actions to use your commit history to tag, generate changelogs, and push a release.'
      end

      def self.return_value
        'The next version calculated from the previous tag.'
      end

      def self.authors
        ['John Pignata', 'Ivan Artemiev']
      end

      def self.available_options
        [
          FastlaneCore::ConfigItem.new(key: :release_tag_type,
                                        description: "Is the release tag lightweight or annotated. Default = lightweight",
                                        default_value: 'lightweight',
                                        verify_block: proc do |value|
                                          UI.user_error!("Parameter tag_type must be lightweight OR annotated.") unless ['lightweight', 'annotated'].include?(value)
                                        end),
          FastlaneCore::ConfigItem.new(key: :release_tag_prefix,
                                       description: "Release tag prefix. Default = v",
                                       default_value: 'v')
        ]
      end

      def self.is_supported?(platform)
        true
      end
    end
  end
end
