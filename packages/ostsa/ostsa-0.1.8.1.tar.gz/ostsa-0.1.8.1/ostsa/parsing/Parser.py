from os.path import dirname, getsize, join

import re

###############################################################################

class Parser(object):
    """A Parser takes a file name and provides utilities for parsing
    information from the file.    
    
    When created, the parsers reads in and stores all of the contents of the
    file in order to optimize the speed of the parsing.
    
    On top of holding the contents of the file, the Parser class can also
    maintain a cache of pertinent information in order to optimize the 
    performance of parsing by preventing duplicated logic. This can be used 
    like so:
    
        parser = Parser('...')
        parser['Lines'] = parser.contents.split()
        if ('Lines' in sample):
            print(sample['Lines'])
    
    This class utilizes the following cache values:
    
        'Contents':       The entire file's contents in the form of a string.
        'Lines':          A list of all of the lines in the file.
        'Words_{regex}':  A list of all of the words in the file split using
                          the regex {regex}.
        'WCount_{word}':  The number of instances found for the word {word} in 
                          the file.
        
    """
    
    # Initialize a static cache to store values that may need to be reused
    # by all instances of the class.
    __cache = {}
    
    @staticmethod
    def load_list(list_file_name, directory=None):
        """Load and return all of the lines from the specified files as a list.
        
        The directory parameter is optional for specifying a base directory.
        
        Once a list is loaded from a file, the list is cached for subsequent
        calls.
        """
        
        # Prepend the directory to the file name if necessary.
        if (directory):
            list_file_name = join(directory, list_file_name)
        
        # If the list is not in the cache, load in the file.
        if (not list_file_name in Parser.__cache):
            try:
                with open(list_file_name, 'rb') as file:
                    Parser.__cache[list_file_name] = file.read().split(b'\r\n')
            except IOError:
                raise IOError('Could not load the file %s' % list_file_name)
                
        return Parser.__cache[list_file_name]
    
    def __init__(self, file_name):
        """Initialize a new parser that parses the file with the specified
        file name.
        """
        
        # Save the file name.
        self._file_name = file_name
        
        # Initialize a cache to store values that may need to be reused.
        self.__cache = {}
        
        # Ensure the file is valid.
        try:
            with open(file_name, 'rb') as file:
                # Store the contents of the file for parsing.
                self['Contents'] = file.read()
                
        except IOError:
            raise ValueError('Invalid file name %s' % file_name)
                    
    def __contains__(self, key):
        """Check if the cache contains an item for the specified key."""
        return key in self.__cache
        
    def __delitem__(self, key):
        """Clear the cached item with the specified key."""
        self.__cache.pop(key, None)
            
    def __getitem__(self, key):
        """Get the cached value for the specified key."""
        return self.__cache[key]
        
    def __setitem__(self, key, value):
        """Set the cached value for the specified key."""
        self.__cache[key] = value        
        
    @property
    def contents(self):
        """Get the entire file as one continuous string."""
        return self['Contents']
        
    @property
    def file_size(self):
        """Get the size of the file."""
        return getsize(self._file_name)
        
    @property
    def lines(self):
        """Get the lines in the file."""
        
        # Cache the lines in the file.
        if (not 'Lines' in self):
            self['Lines'] = self.contents.split(b'\n')
            
        return self['Lines']
        
    @property
    def num_lines(self):
        """Get the number of lines in the file."""
        return len(self.lines)

    def word_counts(self, words, split_pattern=br''):
        """Find the number of occurrences of the specified words.
        
        Each word must be bytes or bytes-like, not a string. You can convert
        a string literal to bytes by prepending a lowercase b before the
        quotation marks like so:
        
            b'Hello'
            
        If you wish to split the words in a file a certain way, you can
        specify the split_pattern as a bytes object containing a regex that
        will be used to split the file contents into a list of words.
        
        The return value will be a list of counts with each count corresponding
        to the passed in word.
        """
        
        # Find the word whose results are not already cached.
        uncached_words = set()
        for word in words:
            
            # Ensure the word's result is not cache'd.
            word_key = 'WCount_%s' % word
            if word_key in self:
                continue
            
            # Add the word to the set.
            uncached_words.add(word)
            
            # Initialize the word's count in the cache.
            self[word_key] = 0
            
        # If there are uncached patterns, they need to be counted.
        if uncached_words:
            
            # Retrieve all of the words in the file.
            file_words = self.words(split_pattern) if split_pattern \
                                                   else self.words()
            
            # Iterate through every word in the file. If a word is in the
            # list of uncached words, increment its count.
            for word in file_words:
                if word and word in uncached_words:
                    word_key = 'WCount_%s' % word
                    self[word_key] += 1
        
        # Return a list of all of the counts.
        return [self['WCount_%s' % word] for word in words]
        
    def words(self, split_pattern=br'\s+'):
        """Get the words in the file.
        
        The split_pattern is a regex string that will determine how the word
        boundaries are defined. The regex string matches whitespace by default.
        """
        
        # Cache the words in the file.
        key = 'Words_%s' % split_pattern
        if (not key in self):
            
            # Split the file contents into words.
            self[key] = [word for word 
                         in re.split(split_pattern, self.contents) 
                         if word != b'']
            
        return self[key]
