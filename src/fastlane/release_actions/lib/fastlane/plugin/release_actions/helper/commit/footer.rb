class Commit
  # Footer provides case insensitive access to a hash. The Conventional Commits spec designates
  # footer tokens are to be treated case insensitively. Rather than doing a linear search of
  # the key space each time, this object uses additional space to store a mapping of lowercase
  # keys to their originally styled version. Lookups are done using the key hash, which then
  # returns another key which is used to return the attribute. When enumerated, Footer will
  # return the original key found in the footer.
  class Footer
    include Enumerable

    def initialize
      @attributes = {}
      @keys = {}
    end

    def each(&block)
      attributes.each(&block)
    end

    def []=(key, value)
      attributes[key] = value
      keys[key.downcase] = key
    end

    def [](key)
      if key?(key)
        attributes[keys[key.downcase]]
      end
    end

    def size
      keys.size
    end

    def empty?
      keys.empty?
    end

    def key?(key)
      keys.key?(key.downcase)
    end

    alias has_key? key?

    private

    attr_accessor :attributes, :keys
  end
end
