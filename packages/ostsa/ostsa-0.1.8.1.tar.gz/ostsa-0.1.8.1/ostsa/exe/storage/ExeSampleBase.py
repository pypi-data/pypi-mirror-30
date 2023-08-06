from . import ExeSample, entropy
from ...parsing import memoize
from ...storage import create_dirs
from math import log, sqrt
from abc import abstractmethod
from operator import itemgetter
from PIL import Image

import mahotas
import numpy as np
import re

###############################################################################

class ExeSampleBase(ExeSample):
    """ExeSampleBase is a base implementation of the ExeSample interface that
    implements the main logic for many of the defined feature methods.
    
    ExeSampleBase is designed to use a specific format that is reasonably
    abstract so that subclasses only need to worry about adapting their
    formats to the base format, and not about implementing the logic for
    extracting the features.
    
    NOTE: When creating a SampleDao to store ExeSamples, you must use ExeSample
          as the sample type, not this class. Since this class does not
          re-include the feature annotations with the feature method
          implementations, the SampleDao will not be able to find all of the
          necessary feature methods.
    """
    
    ###########################################################################
    
    @abstractmethod
    def load_hex_view(self):
        """Load the hex representation of the executable's code section.
        
        The hex view should contain every instruction's address and machine
        code represented as hex digits. Each instruction should start with
        the address (8 digits) and then end with the instruction (32 digits).
        
        Whitespace is allowed between any of the digits, but it will simply
        be removed and only serves to degrade performance. 
        
        The total length of the hex view does not need to be perfectly 
        divisible by 40, as long as the last instruction is the only
        instruction that has fewer than 40 bytes.
        
        The hex view should be returned as a bytes string. Any other format
        is not guaranteed to work.
        
        Subclasses should only define this method, not use it. If a subclass
        wants the results of this method, call the hex_view method.
        """
        pass
    
    @abstractmethod
    def load_sections(self):
        """Load the section information from the executable.
        
        The return value should be a list of tuples representing sections.
        Each tuple should contain the following values in the specified
        order:
            
            The name of the section
            The virtual address that the section starts at
            The size  (in bytes) of the section.
            A bool indicating whether or not the section is code (0x20000000).
        """
        pass
    
    ###########################################################################
    
    def assembly_view(self, include_data=False):
        """Return the formatted assembly view.
        
        If include_data is set to false, sections that do not include
        executable code will be ignored. This is useful for samples that
        contain an extreme amount of data.
        """
        
        # Retrieve all of the instructions and sections.
        instructions = self.instructions()
        sections = self.sections()
        
        if (not instructions):
            return b''
            
        # Find the code sections if necessary.
        if (not include_data):
            code_sections = set(section for section in sections if section[3])
        
        # Print each instruction as a formatted line.
        lines = [] 
        
        sectionIndex = 0
        section = sections[sectionIndex]

        for instruction in instructions:
            
            # Advance to the next section if the instruction is outside the
            # range.
            if (sectionIndex < (len(sections) - 1) and
                instruction[0] >= sections[sectionIndex + 1][1]):
                sectionIndex += 1
                section = sections[sectionIndex]

            # Skip the instruction if necessary.
            if (not include_data and section not in code_sections):
                continue

            # Generate a formatted line for the section.
            address = int(instruction[0])
            bytecode = b' '.join(b'%02x' % b for b in instruction[1])
            line = b'{0:>8}:{1:08x} {2:<24}\t{3}\t{4}'.format(section[0], 
                                                              address,
                                                              bytecode,
                                                              instruction[2], 
                                                              instruction[3])  
            
            lines.append(line)
            
        return b'\r\n'.join(lines)
    
    def bytes(self):
        """Return a list of all bytes contained in the hex view.
        
        Bytes used to represent the addresses of instructions are not included
        due to their lack of usefulness.
        
        Each byte is represented by its decimal value. The special ?? byte is
        represented with a value of -1.
        """
            
        # Remove all spaces from the contents of the hex view.
        contents = self.hex_view()
        
        # Every two hex digits represents a single byte.
        byte_values = [-1 if contents[i:i+2] == b'??' 
                       else int(contents[i:i+2], 16) 
                       for i in range(0, len(contents), 2)]

        # The first four bytes of every 20 bytes contains an address, which
        # are not useful for analysis.
        byte_values = [byte_values[i] for i in range(len(byte_values))
                       if i % 20 >= 4]
            
        return byte_values
        
    def digits(self):
        """Return a list of all of the hex digits in the hex view.
        
        Digits used to represent addresses are included.
        
        Each hex digit is represented as an integer. The special ? digit is 
        represented with a value of -1.
        """
        hex = self.hex_view()
        digits = [-1 if hex[i:i+1] == '?' else int(hex[i:i+1], 16) 
                     for i in range(len(hex))]
            
        return digits
        
    def entropies(self, window_size=10000):
        """Calculate the entropy values for each of the windows in the hex
        file if the window has the specified size.
        
        A list of all of the entropy values calculated for each window will
        be returned.
        """
        
        hex_bytes = self.bytes()
        
        # Ensure there are enough bytes for at least one window.
        if (len(hex_bytes) < window_size):
            raise ValueError(('The window size {0} exceeds the number ' +
                             'of bytes in the file: {1}')
                             .format(window_size, len(hex_bytes)))
                             
        # Retrieve the byte counts for the first window.
        window = hex_bytes[:window_size]
        
        byte_counts = {byte: 0 for byte in range(-1, 256)}
        for byte in window:
            byte_counts[byte] += 1
        
        # Calculate the entropy for the first window.
        current_entropy = entropy(byte_counts.values(), window_size)
        entropy_values = [current_entropy]
        
        # Add the entropy values for the rest of the windows.
        for i in range(1, len(hex_bytes) - window_size):
            
            # Determine which bytes were removed and added.
            removed_byte = hex_bytes[i-1]
            added_byte = hex_bytes[i+window_size]
            
            # If the added and removed bytes are not the same, the entropy 
            # needs to be adjusted.
            if (removed_byte != added_byte):
                
                removed_count = byte_counts[removed_byte]
                added_count = byte_counts[added_byte]
                                
                # Subtract out the old entropy values for the modified bytes.
                p = removed_count / window_size
                if (p > 0):
                    current_entropy += p * log(p, 2)
                                
                p = added_count / window_size
                if (p > 0):
                    current_entropy += p * log(p, 2)
                
                # Adjust the counts.
                removed_count -= 1
                added_count += 1
                
                # Add the new entropy values for the modified bytes.
                p = removed_count / window_size
                if (p > 0):
                    current_entropy -= p * log(p, 2)
                
                p = added_count / window_size
                if (p > 0):
                    current_entropy -= p * log(p, 2)
                    
                byte_counts[removed_byte] = removed_count
                byte_counts[added_byte] = added_count
                
            # Add the entropy value to the list.
            entropy_values.append(current_entropy)
            
        return entropy_values
        
    @memoize
    def hex_view(self):
        """Get the hex view of the executable. This will be returned as a bytes
        string.
        """
        
        # Remove all whitespace.
        return b''.join(self.load_hex_view().split())
        
    def hex_view_formatted(self):
        """Get a formatted version of the hex view."""
        
        # Separate the hex view into lines.
        hex_view = self.hex_view()
        lines = [hex_view[i:i+40] for i in range(0, len(hex_view), 40)]
        
        # Format each line.
        def line_format(line):
            address = line[:8]
            instr = b' '.join(line[i:i+2] for i in range(8, len(line), 2))
            return b' '.join([address, instr])
                              
        lines = [line_format(line) for line in lines]
        
        return b'\r\n'.join(lines)
        
    def image_array(self):
        """Create and return an image array containing a list of grayscale
        pixels generated from each hex digit in the file.
        """
                    
        # Retrieve all of the hex digits in the list.
        # NOTE: ? digits are interpreted as having a value of 0.
        digits = self.digits()
        imgarray = [0 if digit == -1 else digit for digit in digits]
        
        # Each line in a bytes file contains 40 digits. The last line of the
        # file, however, may contain less than 40 digits. In order to create
        # a non-jagged 2D array, we need to reduce the number of pixels to the
        # largest multiple of 40.
        lines = len(imgarray) // 40
        imgarray = imgarray[:lines*40]
        
        # Reshape the array of pixels into a 2D array containing 40 columns
        # and a number of rows equivalent to the number of rows in the file
        # (potentially minus 1 row).
        imgarray = np.reshape(imgarray, (lines, 40))        
            
        # Turn the list into a numpy array.
        imgarray = np.array(imgarray)
        
        return imgarray
        
    @memoize
    def instructions(self):
        """Return a list of all of the assembly instructions in the executable.
        
        This list is generated from the Hex View using Capstone. If Capstone is
        not properly set up, this method will raise an exception.
        
        Each instruction will be a tuple containing the following items:
            
            0 - The virtual address of the instruction (int)
            1 - The bytecode for the instruction (bytearray)
            2 - The mnemonic for the instruction (string)
            3 - The operation string for the instruction, which includes the
                registers used in the instruction (string)
        """
        
        # Retrieve all of the bytes in the hex view. ?? bytes (-1 values) will
        # be replaced with zeroes.
        bytecode = bytes(bytearray(0 if b == -1 else b for b in self.bytes()))
        
        # Separate the bytecode into its respective sections.
        #
        # Note: section[0] = Name of section
        #       section[1] = Base address of section
        #       section[2] = Number of bytes in section
        #       section[3] = True if code, False if data
        sections = self.sections()
        section_code = {section[0]: [] for section in sections}

        i = 0
        for section in sections:
            byte_count = section[2]
            section_code[section[0]] = bytecode[i:i+byte_count]
            i += byte_count
                             
        # Disassemble the bytecode assuming a 32-bit file.
        from capstone import Cs, CS_ARCH_X86, CS_MODE_32
        mode = Cs(CS_ARCH_X86, CS_MODE_32)
        mode.skipdata = True
#        mode.detail = True
        
        # Disassmeble the bytecode for each section.
        # Note: If the section does not contain code, each byte needs to be
        #       disassembled one at a time, otherwise Capstone will interpret
        #       all of it as sets of instructions. Disassembling a single byte
        #       causes Capstone to interpret it as a single db instruction
        #       (Capstone outputs db instructions with a pneumonic of .byte).
        def disassemble(section):
            """Generate the list of instructions for a given section."""

            def instruction(address, bytecode, mnemonic, op_str):
                return (address, bytecode, mnemonic, op_str)
                                
            name, base, _, executable = section
            bytecode = section_code[name]

            if (executable):
                # Note: The properties of the instruction objects returned by
                #       Capstone are unicode strings. For consistency, they
                #       should be converted to byte strings.
                return (instruction(i.address, i.bytes, 
                                    i.mnemonic.encode('latin-1'), 
                                    i.op_str.encode('latin-1'))
                        for i in mode.disasm(bytecode, base))
                
            return (instruction(base+i, [ord(bytecode[i:i+1])], b'.byte', 
                                b'0x%02x' % ord(bytecode[i:i+1])) 
                    for i in range(len(bytecode)))
            
        section_disasm = (disassemble(section) for section in sections)
        return [instruction for disasm in section_disasm 
                            for instruction in disasm]
        
    @memoize
    def sections(self):
        """Return a list of all of the sections in the executable.
        
        Each section is represented by a tuple with the following values:
            
            The name of the section
            The virtual address that the section starts at
            The number of bytes in the section
            A bool indicating whether or not the section is executable
        """
        
        # Load all of the sections.
        sections = self.load_sections()
        
        # Sort the sections by their virtual addresses.
        return sorted(sections, key=itemgetter(1))
        
                
    def strings(self):
        """Return a list of all strings in the file.
        
        Strings are determined by taking by converting all of the bytes in the
        file to their ASCII equivalent characters and separating the sequence
        of characters on "unreadable" characters. In ASCII, characters in the
        range of 32 - 127 are considered readable.
        """

        # Retrieve all of the bytes in the hex file.
        bytes = self.bytes()
        
        # Convert the hex values to decimal values.
        # NOTE: The ?? bytes are useless. Filter them out.
        ascii_values = [byte for byte in bytes if byte != -1]
        
        # The printable range for ASCII characters is 32 - 127. Replace
        # anything outside those bounds with a null to be filtered out.
        characters = [chr(value) if 32 <= value <= 127 else '\0' for value 
                      in ascii_values]
                      
        # Retrieve each string by splitting up sequences of characters by
        # null characters.
        strings = ''.join(characters)
        strings = [string for string in strings.split('\0') 
                   if string != '']
            
        return strings
        
    ###########################################################################
        
    def byte_count(self):
        return len(self.bytes())
        
    def entropy(self):
        return self.entropies(len(self.bytes()))[0]
        
    def entropy_stats(self, window_size=10000):
        
        # Retrieve the list of entropy values.
        entropy_values = self.entropies(window_size)
        
        # Calculate various statistics for the entropy values.
        features = [
            np.mean(entropy_values),
            np.var(entropy_values),
        ]
        
        # Percentiles 0 - 100
        features.extend(np.percentile(entropy_values, i) for i in range(101))
            
        return features
        
    def first_address(self):
        """Return the address of the first byte sequence in the sample's
        hex file.
        """
        
        # The first word in the hex file is the address of the first byte 
        # sequence.
        first_word = self.hex_view()[:8]
        
        # The address is a hexadecimal value. Convert it to decimal.
        return int(first_word, 16)
    
    def four_gram_frequencies(self):
        
        # All possible assembly instruction four grams would surpass 2.6 million
        # possibilities. This would require significant processing power. Due to
        # lack of processing power and to make calculation less memory intensive
        # on most computers, the four gram features include randomly shuffled 
        # combinations of 7 selected opcodes: mov, add, sub, call, mov, pop, and
        # ret.
        
        # From those, the top 331 of this set of combinations are seached in the
        # file and returned. 
        
        instructions = self.instructions()
        instructions = [i[2] for i in instructions]
        file_four_grams = (instructions[i:i+4] for i in range(len(instructions)-4))
        file_four_grams = (b','.join(g) for g in file_four_grams)
        
        # Count occurrences.
        four_grams = ExeSample.four_gram_list()
        
        counts = {four_gram: 0 for four_gram in four_grams}
        for four_gram in file_four_grams:
            if four_gram in counts:
                counts[four_gram] += 1

        return [counts[four_gram] for four_gram in four_grams]
        
    def haralick_features(self):
    
        # Retrieve an image representation of the file.
        img = self.image_array()
        
        # Run Haralick features analysis on the image.
        features = mahotas.features.haralick(img)
        return list(features.flatten())
        
    def instruction_counts(self):
        
        # Note: Dictionaries have a constant time complexity for access and
        #       insertion. Using a dictionary to hold the counts effectively
        #       reduces the time complexity of this method from O(n^2) to
        #       O(n).
        counts = {i: 0 for i in ExeSample.instruction_list()}
                  
        # Each instruction is identified by its mnemonic, which is the 3rd
        # element for every instruction.
        mnemonics = (i[2] for i in self.instructions())
        for mnemonic in mnemonics:
            if (mnemonic in counts):
                counts[mnemonic] += 1

        # We need to reference the instructions list again to make sure the 
        # counts are in the correct order, since dictionaries make no
        # guarantees when it comes to order.
        return [counts[i] for i in ExeSample.instruction_list()]
    
    def instruction_total(self):
        
        # Invoking instructions sends back a list of all assembly instrutions
        # in the file. Finding the length of this list will find the total
        # number of instructions in the assembly view made by Capstone.
        return len(self.instructions())
        
    def local_binary_patterns(self):
        
        # Retrieve an image representation of the file.
        img = self.image_array()
        
        # Find the 13 Local Binary Pattern features from the image.
        lbppoints = mahotas.features.lbp(img, 10, 10, ignore_zeros=False)
        
        return lbppoints.tolist()
        
    def one_gram_frequencies(self, *one_grams):
        
        # Default one_grams:
        if not one_grams:
            one_grams = range(256)
        
        # Validate one_grams:
        else:
            
            # Type check
            non_ints = sum(type(item) is not int for item in one_grams)
            if (non_ints > 0):
                raise TypeError('1-gram values must be integer values')
                
            # Range check
            invalid_ranges = sum(not 0 <= value <= 255 for value in one_grams)
            if (invalid_ranges > 0):
                raise ValueError('1-grams must be in the range 0 - 255 '
                                 + 'inclusive')
                                                                  
        # Every byte represents a one-gram.
        # NOTE: ?? bytes are ignored.
        file_one_grams = [byte for byte in self.bytes() if byte != -1]
            
        # Retrieve the counts for each one gram.
        counts = {one_gram: 0 for one_gram in one_grams}
        for one_gram in file_one_grams:
            if (one_gram in counts):
                counts[one_gram] += 1
                
        return [counts[one_gram] for one_gram in one_grams]  

    def register_counts(self):
        
        # The registers used for each instruction are found in the op string
        # for the instruction, which is the 4th element.
        op_strs = (i[3] for i in self.instructions())
        
        # Registers only contain valid word characters. We can use this fact
        # to our advantage by splitting each op string into its valid words.
        # This allows us to use the dictionary counting technique instead of
        # using find in a nested loop, changing the time complexity from O(n^2)
        # to O(n).
        regex = re.compile(br'(^|\b)[^\w]+(\b|$)')
        tokens = [t for op_str in op_strs 
                    for t in regex.split(op_str) 
                    if  t != b'']
                
        # Dictionary counting method. See instruction_counts for details.
        counts = {r: 0 for r in ExeSample.register_list()}
        for token in tokens:
            if (token in counts):
                counts[token] += 1

        return [counts[r] for r in ExeSample.register_list()]

    def section_sizes(self):
        
        # Construct a dictionary of section sizes.
        section_sizes = {section[0]: section[2] for section in self.sections()}
                         
        return [section_sizes.get(section, 0) 
                for section in ExeSample.section_list()]
        
    def string_lengths(self, *bins):
        """Returns a histogram containing the count of all of the strings in
        each specified bin.
        
        The bins parameter should be a list of tuples containing 2 integers
        that define the range for each bin. The first number of each tuple
        should define the lower range (inclusive) and the second number should
        define the higher range (exclusive).
        
        On top of the specified bins, there will always be a bin countaining
        the count of all strings that didn't fall into any other bins. The
        count for this bin will be the last value in the returned list.
        """
        
        # Default bin_boundaries:
        if (not bins):
            bins = [(0, 10), (10, 30), (30, 60), (60, 90), (0, 100),
                    (100, 150), (150, 250), (250, 400), (400, 600), (600, 900),
                    (900, 1300), (1300, 2000), (2000, 3000), (3000, 6000), 
                    (6000, 150000)]
                    
        # If there were specific bin values passed, ensure they are structured
        # correctly.
        else:
            
            # Validate each bin.
            for bin in bins:
                
                # Ensure each item is a tuple.
                if (type(bin) is not tuple):
                    raise TypeError('Bins must be represented with tuples')
                    
                # Ensure each tuple has only two values.
                if (len(bin) != 2):
                    raise ValueError('Bin tuples must contain exactly 2 ints')
                    
                # Ensure both values are integers.
                if (type(bin[0]) is not int or type(bin[1]) is not int):
                    raise TypeError('Bin tuples must contain int values')
        
        # Retrieve all of the strings.
        strings = self.strings()
        
        # Categorize each string into a bin.
        # NOTE: A single string can be classified into multiple bins.
        counts = {bin: 0 for bin in bins}
        uncategorized = 0
        for string in strings:
            
            # Keep track if a string is categorized into at least one bin.
            categorized = False
            
            # Check if the string fits in each bin.
            for bin in bins:
                
                # Count the string if its length fits in the range of the bin.
                if bin[0] <= len(string) < bin[1]:
                    counts[bin] += 1
                    
                # Mark the bin as categorized.
                categorized = True
                
            # Check if the string was uncategorized.
            if (not categorized):
                uncategorized += 1
                
        # Return the count for every bin.
        counts = [counts[bin] for bin in bins]
        counts.append(uncategorized)
        
        return counts
    
    def symbol_counts(self):
        
        # The symbols (+, -, [, *) used for each instruction are found in the 
        # op string for the instruction, which is the 4th element.
        op_strs = (i[3] for i in self.instructions())
        
        # We can split each op string into its specific symbols. We can use 
        # this fact to our advantage by splitting each op string into its valid 
        # symbols.This allows us to use the dictionary counting technique 
        # instead of using find in a nested loop, changing the time complexity
        # from O(n^2)to O(n).
        regex = re.compile(br'[^-+[*]+')
        tokens = [t for op_str in op_strs 
                    for t in regex.split(op_str) 
                    if  t != b'']
                
        # Dictionary counting method. See instruction_counts for details.
        counts = {r: 0 for r in ExeSample.symbol_list()}
        for token in tokens:
            if (token in counts):
                counts[token] += 1

        return [counts[r] for r in ExeSample.symbol_list()]       
        
        
    def two_gram_frequencies(self):
        
        # Filter out all of the ?? bytes.
        sample_bytes = [byte for byte in self.bytes() if byte != -1]
             
        # A 2-gram consists of 2 bytes. Since each byte is already in decimal
        # format, we need to do a minor calculation to combine the two bytes.
        # The most significant byte can be viewed as one large value in the
        # 3rd digit's place in hex. This means we can simply multiply that
        # leftmost byte by 16^2 (256) and add it to the rightmost byte.
        file_two_grams = [sample_bytes[i] * 256 + sample_bytes[i+1] for i 
                                              in range(len(sample_bytes)-3)]
        
        # Count occurrences.
        two_grams = range(256**2)
        counts = {two_gram: 0 for two_gram in two_grams}
        for two_gram in file_two_grams:
            counts[two_gram] += 1

        return [counts[two_gram] for two_gram in two_grams]
        
###############################################################################
        
    def save_asm_file(self, file_name, include_data=False):
        """Save the assembly view to a file with the specifed name.
        
        If include_data is set to false, sections that don't contain executable
        code will not be included in the file.
        """
        
        with open(file_name, 'wb') as file:
            file.write(self.assembly_view(include_data=include_data))

    def save_hex_file(self, file_name):
        """Saves the formatted hex view to a file with the specified name."""
        
        with open(file_name, 'wb') as file:
            file.write(self.hex_view_formatted())
            
    def save_image(self, file_name, color_bound1=0x000000, 
                   color_bound2=0xFFFFFF, aspect_ratio=1.0):
        """Save the image generated from the hex view to the specified file.
        The image will be saved as a .png file. The .png will be appended to
        the end of the specified file name, so an extension should not be
        included.
        
        color_bound1 is the color of a pixel representing a hex digit of 0.
        
        color_bound2 is the color of a pixel representing a hex digit of F.
        
        The aspect_ratio should be the desired width to height ratio of the
        image. A value greater than 1 will yield an image that is wider than
        it is tall, while a value less than 1 will yield an image that is
        taller than it is wide. The default value is 1, which will result in
        a square image.
        """
        
        # Retrieve component bases and ranges from the color bounds.
        r_base = (color_bound1 >> 16) & 0xFF
        g_base = (color_bound1 >> 8) & 0xFF
        b_base = color_bound1 & 0xFF
        
        r_range = ((color_bound2 >> 16) & 0xFF) - r_base
        g_range = ((color_bound2 >> 8) & 0xFF) - g_base
        b_range = (color_bound2 & 0xFF) - b_base
        
        # Each of the items in the image array is a value between 0 and 15.
        # Each value can be used as a ratio to determine the intermediate
        # value for each component.
        def pixel(hex_value):
            return (r_base + int(hex_value / 15 * r_range),
                    g_base + int(hex_value / 15 * g_range),
                    b_base + int(hex_value / 15 * b_range))
                    
        pixels = [pixel(float(value)) for row in self.image_array() for value in row]
                
        # Calculate the dimensions of the image based on the aspect ratio.
        height = sqrt(len(pixels) / float(aspect_ratio))
        width  = len(pixels) / height

        height = int(height)
        width  = int(width)
        
        # Save to a png file.
        image = Image.new('RGB', (width, height))
        image.putdata(pixels[:width*height])
        
        create_dirs(file_name)
        image.save('%s.png' % file_name)
        
         
        
