from . import ExeSampleBase
from ...parsing import memoize
from os.path import basename, exists, splitext

import re

###############################################################################

class ExeKaggleSample(ExeSampleBase):
    """ExeKaggleSample represents the samples retrieved from the Microsoft
    Malware Classification Challenge hosted on Kaggle:
    
        https://www.kaggle.com/c/malware-classification
    
    For each sample, a .bytes and .asm file is supplied. The .bytes file
    contains the hex view that is required by the ExeSampleBase, and the .asm
    file contains the disassembled binary (disassembled by IDA). 
    
    The .bytes file contains no header information to ensure the sterility of
    the samples. Any data that would normally be in the header needs to be
    retrieved from the disassembly.
    """
    
    def __init__(self, bytes_file_path, asm_file_path):
        """Initialize a sample represented by the specified bytes file and the
        specified asm ."""
        
        # Ensure the file exists.
        if (not exists(bytes_file_path)):
            raise ValueError('The file {0} could not be found'.format(
                                                              bytes_file_path))
                                                              
        # NOTE: The files should only be opened when the contents are
        #       absolutely needed. Loading the contents in the constructor
        #       could slow down batch operations.
        self._bytes_file_path = bytes_file_path
        self._asm_file_path = asm_file_path
        
        # Use the name of the file without the path or extension as the ID for
        # the sample.
        self._id = splitext(basename(bytes_file_path))[0]

    @memoize
    def assembly_contents(self):
        """Gets the contents of the assembly file."""
        
        with open(self._asm_file_path, 'rb') as asm_file:
            return asm_file.read()
            
    @memoize
    def image_base(self):
        """Gets the image base of the executable from the assembly file as a
        decimal number.
        """
        
        # The image base is written in a comment by IDA in the assembly file.
        # The comment has roughly the following structure:
        #
        #       ; Imagebase    : {Base Address}
        #
        # where {Base Address} is the base address in hex (minus the 0x 
        # prefix).
        
        # Regex for finding the base address. Captures the actual address in a
        # group called 'address'.
        regex = re.compile(r';\s+Imagebase\s+:\s+(?P<address>\d+)')
        
        address = regex.search(self.assembly_contents()).group('address')
        return int(address, 16)
        
    def load_hex_view(self):
        
        # Load the bytes file in.
        with open(self._bytes_file_path, 'rb') as bytes_file:
            return bytes_file.read()
            
    def load_sections(self):
        
        # Every section in the assembly file is marked with a comment in the
        # following format:
        #
        #   ; Section {Number}. (virtual address {Address})
        #
        # where {Number} is the number of the section and {Address} is the
        # virtual address for the section represented in hex (without the 0x
        # prefix).
        #
        # At the beginning of every line in a section (including the line with
        # the comment), the section name can be found in the following format:
        #
        #    {Name}:{Address}
        #
        # where {Name} is the name of the section and {Address} is the hex
        # address of the instruction on the line.
        #
        # Underneath the line displaying the section there is a line that shows
        # the virtual size:
        #
        #   ; Virtual size : {Hex Address} ( {Decimal Address}.)
        #
        # Three lines under the virtual address line is a line that displays
        # the special flag describing the section:
        #
        #   ; Flags {Hex Flag}: {Flag Meaning}
        #
        # All of these can easily be extracted using regex patterns.
        
        # Section Line: name = section name, address = hex virtual address
        section_regex = re.compile((br'(?P<name>\.\w+):(?P<address>\w+).+'
                                    br';\s+Section\s+\d+'))
        
        # Virtual size line: size = hex virtual size
        virtual_size_regex = re.compile((br';\s+Virtual\s+size\s+'
                                         br':\s+(?P<size>\w+)'))
        
        # Flag line: 
        flag_regex = re.compile(br';\s+Flags\s+(?P<flag>\w+)')
        
        # Find all of the section lines first.
        sections = []
        asm = self.assembly_contents()
        for match in section_regex.finditer(asm):
            
            # Find the name and address.            
            name = match.group('name')
            address = int(match.group('address'), 16)
            
            # Find the virtual size.
            match = virtual_size_regex.search(asm, match.end())
            virtual_size = int(match.group('size'), 16)
                        
            # Find the flag.
            match = flag_regex.search(asm, match.end())
            flag = int(match.group('flag'), 16)
            executable = bool(flag & 0x20000000)
            
            # Add the section.
            sections.append([name, address, virtual_size, executable])

        return sections
            
            
        
        
