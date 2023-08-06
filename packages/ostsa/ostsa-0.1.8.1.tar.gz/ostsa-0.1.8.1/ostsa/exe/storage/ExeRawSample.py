from . import ExeSampleBase
from ...parsing import memoize

import os
import pefile
import uuid

###############################################################################

class ExeRawSample(ExeSampleBase):
    """An ExeRawSample represents a sample that retrieves its features from
    a raw Windows Executable (.exe) file.
    """
    
    def __init__(self, file_path=None, data=None):
        """Initialize a new ExeRawSample that retrieves its features from the
        specified Windows Executable (.exe) file.
        
        If data is specified in place of a file path, the data will be used
        as the contents of the Windows Executable file to be used instead of
        loading a file. The data should be the file's contents formatted as
        a series of unencoded bytes.
        """
        
        # NOTE: The file should only be opened when the contents are
        #       absolutely needed. Loading the contents in the constructor
        #       could slow down batch operations.
        self._file_path = file_path
        self._data = data
        
        # If a file was supplied, ensure it exists.
        if (file_path):
        
            if (not os.path.exists(file_path)):
                raise ValueError('The file %s could not be found' % file_path)

            # Use the name of the file without the path or extension as the ID 
            # for the sample.
            self._id = os.path.splitext(os.path.basename(file_path))[0]

        # If a file was not supplied, generate random ID for the file.
        else:
            self._id = uuid.uuid4()
        
    @memoize
    def pe(self):
        """Gets the PE wrapper object that can be used to parse information
        from the executable.
        """
        return pefile.PE(self._file_path, self._data)
        
    def load_hex_view(self):
        
        # Retrieve all of the sections.
        sections = self.pe().sections
        
        # Construct the hex view string using the code in the sections.
        hex_view = b""
        for section in sections:
            
            # Get base address of section
            base_address = self.pe().OPTIONAL_HEADER.ImageBase \
                           + section.VirtualAddress
            
            # Get bytes representing section
            data = section.get_data()
            section_data = [b'%02x' % ord(data[i:i+1]) for i 
                            in range(len(data))]
            
            # Break the bytes into lines, with each line containing 16 bytes.
            lines = [b''.join(section_data[i:i+16]) for i 
                     in range(0, len(section_data), 16)]
                     
            # Every line should have the address in front of it. The address
            # should be incremented by 16 for every line.
            lines = [b'%08x%s' % (base_address+(i*16), lines[i]) 
                     for i in range(len(lines))]
                                
            hex_view += b''.join(lines)
            
        return hex_view
        
    def load_sections(self):
        
        # Retrieve all sections.
        sections = self.pe().sections

        # Retrieve the name, address, size, and indicator of executable code
        # for each section.
        base_address = self.pe().OPTIONAL_HEADER.ImageBase
        return [(s.Name.rstrip(b'\x00'), s.VirtualAddress + base_address, 
                 s.Misc_VirtualSize, s.IMAGE_SCN_MEM_EXECUTE) 
                 for s in sections]
        
    def validate(self):
        """Check if the supplied constructor arguments represent a valid
        Windows Executable file.
        
        If valid, return True, otherwise, return False.
        """
        
        # If the PE file successfully loads, the file is valid.
        try:
            return self.pe().is_exe() or self.pe().is_dll()
            
        except:
            return False
            
        
