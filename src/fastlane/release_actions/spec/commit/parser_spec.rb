require 'spec_helper'
require 'helper/commit/parser'
require 'helper/commit/commit'
require 'helper/commit/commits'

describe Commit::Parser do
  let(:parser) { Commit::Parser.new(msg) }
  let(:commit) { parser.commit }

  before { parser.parse }

  context 'a one-line commit message' do
    let(:msg) { 'feat: Allow users to reset passwords' }

    example { expect(commit.type).to eq(:feat) }
    example { expect(commit.subject).to eq('Allow users to reset passwords') }
  end

  context 'a mixed-case type in a one-line commit message' do
    let(:msg) { 'FiX: Address bugs I created' }

    example { expect(commit.type).to eq(:fix) }
  end

  context 'a one-line commit message that is a breaking change' do
    let(:msg) { 'feat!: New API' }

    example { expect(commit.type).to eq(:feat) }
    example { expect(commit.subject).to eq('New API') }
    example { expect(commit.breaking_change).to eq('New API') }
  end

  context 'a one-line commit message with a scope' do
    let(:msg) { 'fix(testutils): Fix flakiness in suite' }

    example { expect(commit.type).to eq(:fix) }
    example { expect(commit.subject).to eq('Fix flakiness in suite') }
    example { expect(commit.scope).to eq('testutils') }
  end

  context 'a malformed one-line commit message' do
    let(:msg) { 'fix:foo' }

    example { expect(commit.type).not_to eq(:foo) }
    example { expect(commit.subject).to eq('fix:foo') }
  end

  context 'a multi-line commit message with breaking changes' do
    let(:msg) do
      <<~TEXT
        feat: completely refactor the API

        BREAKING CHANGE: The old API won't work, sry.
      TEXT
    end

    example { expect(commit.type).to eq(:feat) }
    example { expect(commit.subject).to eq('completely refactor the API') }
    example { expect(commit.breaking_change).to eq('The old API won\'t work, sry.') }
    example { expect(commit.footer.size).to eq(1) }
    example { expect(commit.footer['BREAKING CHANGE']).to eq('The old API won\'t work, sry.') }
  end

  context 'a multi-line commit message with footer items' do
    let(:msg) do
      <<~EOF
        feat: completely refactor the API

        BREAKING CHANGE: The old API won't work, sry.
        Reviewed-by: Dwayne Johnson
        Refs #133
      EOF
    end

    example { expect(commit.footer.size).to eq(3) }
    example { expect(commit.footer['BREAKING CHANGE']).to eq('The old API won\'t work, sry.') }
    example { expect(commit.footer['Reviewed-by']).to eq('Dwayne Johnson') }
    example { expect(commit.footer['Refs']).to eq('#133') }
  end

  context 'a multi-line commit message with a multi-line footer item' do
    let(:msg) do
      <<~EOF
        feat: completely refactor the API

        BREAKING CHANGE: The old API won't work, sry. The reason why is because
        I broke it. Look, I'm sorry, ok?
        Fired-By: Boss
      EOF
    end

    example { expect(commit.footer.size).to eq(2) }
    example { expect(commit.footer['BREAKING CHANGE']).to eq("The old API won't work, sry. The reason why is because\nI broke it. Look, I'm sorry, ok?") }

    describe 'footer keys are case insensitive' do
      example { expect(commit.footer['Fired-By']).to eq('Boss') }
      example { expect(commit.footer['fired-by']).to eq('Boss') }
      example { expect(commit.footer['fIrEd-BY']).to eq('Boss') }
      example { expect(commit.footer).to have_key('Fired-By') }
      example { expect(commit.footer).to have_key('fired-by') }
      example { expect(commit.footer).to have_key('fIrEd-BY') }
    end
  end

  context 'a multi-line commit message with a body' do
    let(:msg) do
      <<~EOF
        feat: Add some snazzy new feature

        Feature is new. Feature is also snazzy.

        Closes: #123
      EOF
    end

    example { expect(commit.body).to eq('Feature is new. Feature is also snazzy.') }
    example { expect(commit.footer['Closes']).to eq('#123') }
  end

  context 'a multi-line commit that does not conform to the spec' do
    let(:msg) do
      <<~EOF
        this is a: subject without a type or scope

        this is a body
      EOF
    end

    example { expect(commit.type).to eq(:change) }
    example { expect(commit.scope).to be(nil) }
    example { expect(commit.subject).to eq('this is a: subject without a type or scope') }
    example { expect(commit.body).to eq('this is a body') }
    example { expect(commit.footer).to be_empty }
  end
end
