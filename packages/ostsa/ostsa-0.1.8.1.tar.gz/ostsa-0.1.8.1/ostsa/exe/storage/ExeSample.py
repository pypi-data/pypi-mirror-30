from abc import ABCMeta, abstractmethod
from math import log

from ...storage import Sample, feature

###############################################################################

def entropy(counts, window_size):
    """Retrieve the entropy for a window with the specified counts and window
    sizes.
    
    The counts should be a list of the counts for each of the distinct items
    in the window.
    
    The return value will be between 0 (order) and 8 (randomness).
    
    This is the standard function that should be used to calculate entropy in
    all ExeSample implementations in order to keep consistency.
    """
    
    entropies = [float(count) / float(window_size) * \
                 log(float(count) / float(window_size), 2) 
                 for count in counts if count > 0]
    
    return -sum(entropies)

###############################################################################

class ExeSample(Sample):
    """ExeSample is the base class that defines all of the features a Windows
    Executable sample should contain.
    
    ExeSample is abstract and does not implement any of the feature methods
    defined in it. The purpose of this class is to provide a universal set
    of features that should be parsed from any format of a Windows Executable
    (i.e. Binary files, disassembled files, etc.).
    """
    
    __metaclass__ = ABCMeta
    
    ###########################################################################
    
    @staticmethod
    def instruction_list():
        """Get the list of mnemonics for all of the instructions to be used
        in features involving specific specific instructions.
        """
        
        return [b'add', b'al', b'bt', b'call', b'cdq', b'cld', b'cli', b'cmc', 
                b'cmp', b'const', b'cwd', b'daa', b'.byte', b'dec', b'endp', 
                b'ends', b'faddp', b'fchs', b'fdiv', b'fdivp', b'fdivr', 
                b'fild', b'fistp', b'fld', b'fstcw', b'fstcwimul', b'fstp', 
                b'fword', b'fxch', b'imul', b'in', b'inc', b'ins', b'int3', 
                b'jb', b'je', b'jg', b'jge', b'jl', b'jmp', b'jnb', b'jno', 
                b'jnz', b'jo', b'jz', b'lea', b'loope', b'mov', b'movzx', 
                b'mul', b'near', b'neg', b'not', b'or', b'out', b'outs', 
                b'pop', b'popf', b'proc', b'push', b'pushf', b'rcl', b'rcr', 
                b'rdtsc', b'rep', b'ret', b'retn', b'rol', b'ror', b'sal', 
                b'sar', b'sbb', b'scas', b'setb', b'setle', b'setnle', 
                b'setnz', b'setz', b'shl', b'shld', b'shr', b'sidt', b'stc', 
                b'std', b'sti', b'stos', b'sub', b'test', b'wait', b'xchg', 
                b'xor']
                
    @staticmethod
    def register_list():
        """Get the list of all registers to be used for features involving
        specific registers.
        """
        
        return [b'edx', b'esi', b'es', b'fs', b'ds', b'ss', b'gs', b'cs', 
                b'ah', b'al', b'ax', b'bh', b'bl', b'bx', b'ch', b'cl', b'cx', 
                b'dh', b'dl', b'dx', b'eax', b'ebp', b'ebx', b'ecx', b'edi', 
                b'esp']
    
    @staticmethod
    def symbol_list():
        """Get the list of all symbols to be used for features involving
        specific symbols.
        
        Only one bracket is present since its paired bracket is the same count.
        """
        
        return [b'+', b'-', b'*', b'[']
    
    @staticmethod
    def section_list():
        """Get the list of all of the section names to be used for features
        involving specific sections.
        """
        
        return ['.bss', '.data', '.edata', '.idata', '.rdata', '.rsrc', 
                '.text', '.tls', '.reloc']
        
    @staticmethod
    def four_gram_list():
        """Get the list of all of the 4 four_grams that are to be used for the 
        four_gram feature
        """
        
        return [b'ret,ret,mov,add',
                b'mov,pop,pop,push',
                b'mov,sub,call,call',
                b'add,call,add,call',
                b'pop,push,call,add',
                b'mov,mov,sub,ret',
                b'call,ret,add,call',
                b'push,ret,push,sub',
                b'call,push,ret,mov',
                b'push,sub,mov,add',
                b'add,mov,pop,push',
                b'ret,ret,ret,call',
                b'add,push,sub,push',
                b'call,ret,call,add',
                b'add,add,add,sub',
                b'sub,add,sub,add',
                b'mov,mov,sub,push',
                b'push,pop,pop,mov',
                b'sub,add,push,call',
                b'sub,push,add,call',
                b'mov,mov,add,ret',
                b'sub,mov,push,mov',
                b'add,call,ret,add',
                b'sub,sub,mov,ret',
                b'push,pop,sub,call',
                b'add,sub,ret,push',
                b'sub,call,pop,sub',
                b'sub,ret,call,add',
                b'push,mov,push,pop',
                b'sub,ret,push,mov',
                b'mov,sub,add,mov',
                b'call,push,call,mov',
                b'sub,call,sub,mov',
                b'pop,ret,mov,ret',
                b'add,mov,push,mov',
                b'mov,sub,mov,push',
                b'pop,mov,add,push',
                b'pop,push,call,call',
                b'mov,ret,mov,pop',
                b'pop,mov,mov,add',
                b'add,call,add,ret',
                b'call,mov,pop,call',
                b'mov,add,push,add',
                b'ret,call,add,pop',
                b'ret,ret,push,ret',
                b'push,add,sub,call',
                b'pop,mov,ret,mov',
                b'sub,pop,pop,call',
                b'add,pop,push,add',
                b'pop,call,mov,pop',
                b'call,pop,mov,sub',
                b'mov,add,pop,call',
                b'sub,add,ret,add',
                b'call,call,mov,sub',
                b'pop,call,mov,push',
                b'mov,call,push,add',
                b'push,add,push,ret',
                b'add,mov,call,mov',
                b'pop,ret,push,add',
                b'push,add,ret,pop',
                b'sub,call,mov,add',
                b'ret,sub,push,pop',
                b'pop,ret,add,ret',
                b'ret,pop,pop,ret',
                b'sub,sub,pop,ret',
                b'push,pop,push,mov',
                b'mov,pop,sub,ret',
                b'call,pop,mov,call',
                b'add,push,sub,ret',
                b'mov,call,add,mov',
                b'add,sub,sub,mov',
                b'sub,add,mov,mov',
                b'mov,mov,push,sub',
                b'pop,pop,add,pop',
                b'sub,add,call,push',
                b'call,sub,call,push',
                b'sub,call,call,mov',
                b'sub,sub,ret,pop',
                b'mov,add,add,mov',
                b'push,mov,mov,add',
                b'mov,add,mov,add',
                b'mov,push,pop,add',
                b'push,ret,pop,pop',
                b'sub,push,push,sub',
                b'sub,ret,push,call',
                b'mov,ret,add,add',
                b'pop,ret,pop,add',
                b'ret,mov,add,mov',
                b'call,call,add,sub',
                b'mov,push,push,push',
                b'push,pop,pop,pop',
                b'pop,push,add,push',
                b'ret,ret,sub,ret',
                b'call,add,pop,add',
                b'mov,pop,mov,pop',
                b'push,ret,push,mov',
                b'sub,pop,mov,add',
                b'ret,push,pop,mov',
                b'pop,sub,mov,mov',
                b'pop,mov,push,ret',
                b'push,ret,call,push',
                b'pop,call,sub,add',
                b'sub,mov,pop,push',
                b'add,pop,pop,push',
                b'sub,call,ret,pop',
                b'mov,call,pop,pop',
                b'add,pop,pop,mov',
                b'push,pop,sub,push',
                b'pop,add,ret,call',
                b'mov,push,call,call',
                b'push,mov,add,pop',
                b'call,mov,push,push',
                b'add,pop,mov,call',
                b'call,ret,call,ret',
                b'call,pop,mov,add',
                b'call,pop,mov,mov',
                b'pop,sub,add,mov',
                b'add,sub,pop,call',
                b'ret,call,mov,call',
                b'add,add,sub,add',
                b'push,ret,call,add',
                b'sub,push,mov,pop',
                b'add,mov,sub,push',
                b'push,sub,pop,mov',
                b'sub,pop,ret,mov',
                b'pop,sub,push,push',
                b'mov,mov,pop,add',
                b'pop,sub,call,add',
                b'pop,add,push,ret',
                b'ret,ret,add,add',
                b'push,add,call,push',
                b'push,push,push,push',
                b'pop,add,call,ret',
                b'sub,pop,push,pop',
                b'add,ret,mov,ret',
                b'call,call,call,add',
                b'pop,ret,sub,mov',
                b'add,sub,sub,sub',
                b'ret,mov,ret,add',
                b'sub,sub,sub,add',
                b'add,mov,push,push',
                b'pop,sub,sub,pop',
                b'pop,pop,pop,mov',
                b'call,ret,mov,ret',
                b'call,call,ret,call',
                b'push,sub,call,call',
                b'call,push,ret,ret',
                b'push,call,ret,ret',
                b'sub,mov,ret,pop',
                b'pop,add,pop,mov',
                b'push,call,pop,ret',
                b'push,call,call,ret',
                b'pop,ret,mov,add',
                b'pop,push,ret,mov',
                b'ret,add,add,ret',
                b'call,ret,ret,add',
                b'call,pop,sub,sub',
                b'mov,mov,add,sub',
                b'sub,pop,ret,pop',
                b'sub,call,pop,add',
                b'push,ret,ret,pop',
                b'sub,ret,call,call',
                b'ret,ret,sub,pop',
                b'sub,sub,push,sub',
                b'sub,add,push,sub',
                b'sub,add,push,add',
                b'pop,ret,ret,call',
                b'add,call,pop,sub',
                b'ret,ret,push,push',
                b'mov,mov,push,add',
                b'push,call,mov,pop',
                b'push,call,push,push',
                b'add,push,ret,pop',
                b'push,call,sub,call',
                b'call,add,push,ret',
                b'add,mov,mov,pop',
                b'add,add,add,pop',
                b'call,push,sub,push',
                b'push,sub,sub,add',
                b'ret,sub,sub,call',
                b'mov,pop,call,pop',
                b'mov,add,push,mov',
                b'call,pop,call,ret',
                b'push,ret,sub,add',
                b'add,sub,pop,add',
                b'call,push,call,add',
                b'push,sub,call,push',
                b'add,push,pop,mov',
                b'ret,push,call,pop',
                b'add,sub,sub,call',
                b'pop,push,call,ret',
                b'call,mov,ret,mov',
                b'call,ret,ret,sub',
                b'push,push,mov,mov',
                b'mov,call,add,add',
                b'mov,pop,mov,call',
                b'ret,add,add,mov',
                b'push,call,mov,ret',
                b'ret,mov,call,push',
                b'call,ret,sub,ret',
                b'pop,sub,add,ret',
                b'mov,ret,sub,call',
                b'add,push,mov,ret',
                b'push,push,add,sub',
                b'add,pop,call,pop',
                b'sub,push,pop,push',
                b'pop,call,ret,add',
                b'call,add,mov,call',
                b'call,sub,push,ret',
                b'push,ret,sub,push',
                b'ret,push,ret,sub',
                b'call,ret,mov,call',
                b'push,ret,push,add',
                b'add,pop,call,sub',
                b'push,push,pop,call',
                b'pop,mov,pop,mov',
                b'mov,mov,ret,push',
                b'mov,add,ret,pop',
                b'pop,add,ret,mov',
                b'add,push,mov,mov',
                b'sub,pop,mov,mov',
                b'add,mov,mov,push',
                b'call,pop,push,ret',
                b'call,pop,push,sub',
                b'sub,sub,call,mov',
                b'ret,pop,pop,mov',
                b'push,push,call,push',
                b'add,ret,call,mov',
                b'sub,ret,mov,add',
                b'call,push,call,push',
                b'pop,sub,push,call',
                b'push,push,add,call',
                b'pop,pop,add,add',
                b'sub,pop,pop,add',
                b'mov,add,sub,ret',
                b'push,push,add,mov',
                b'push,ret,add,pop',
                b'ret,pop,call,add',
                b'pop,add,add,ret',
                b'call,sub,add,pop',
                b'mov,push,add,call',
                b'ret,mov,call,add',
                b'ret,add,sub,sub',
                b'call,mov,sub,push',
                b'call,sub,add,call',
                b'call,pop,add,ret',
                b'ret,call,call,mov',
                b'pop,call,sub,sub',
                b'mov,mov,call,ret',
                b'ret,ret,sub,sub',
                b'mov,ret,call,call',
                b'add,call,sub,call',
                b'pop,sub,sub,sub',
                b'mov,mov,sub,call',
                b'ret,call,sub,ret',
                b'mov,call,pop,add',
                b'ret,ret,add,mov',
                b'mov,mov,ret,mov',
                b'sub,ret,call,pop',
                b'call,pop,sub,mov',
                b'call,ret,sub,mov',
                b'ret,call,push,call',
                b'call,add,add,ret',
                b'mov,ret,pop,call',
                b'sub,push,pop,ret',
                b'add,add,mov,mov',
                b'sub,pop,push,push',
                b'add,call,ret,sub',
                b'mov,call,mov,mov',
                b'call,call,pop,pop',
                b'sub,push,sub,add',
                b'ret,pop,add,call',
                b'call,add,push,add',
                b'push,call,add,push',
                b'pop,add,pop,add',
                b'mov,pop,pop,add',
                b'sub,add,push,mov',
                b'mov,pop,ret,call',
                b'call,mov,mov,sub',
                b'add,push,push,add',
                b'sub,pop,push,mov',
                b'call,add,sub,call',
                b'mov,mov,mov,pop',
                b'pop,add,ret,add',
                b'sub,push,sub,mov',
                b'call,add,sub,mov',
                b'call,push,sub,sub',
                b'sub,add,add,pop',
                b'ret,add,pop,add',
                b'add,call,pop,push',
                b'add,add,ret,mov',
                b'call,sub,sub,ret',
                b'pop,pop,sub,add',
                b'ret,mov,add,sub',
                b'pop,pop,sub,pop',
                b'call,ret,add,sub',
                b'call,sub,mov,ret',
                b'mov,sub,call,push',
                b'ret,sub,push,call',
                b'ret,push,ret,add',
                b'mov,ret,sub,ret',
                b'mov,ret,mov,add',
                b'push,pop,sub,ret',
                b'mov,pop,push,call',
                b'sub,push,pop,call',
                b'push,sub,call,pop',
                b'add,ret,mov,pop',
                b'push,push,sub,pop',
                b'pop,ret,call,push',
                b'push,mov,pop,mov',
                b'pop,sub,pop,push',
                b'ret,ret,call,add',
                b'ret,sub,pop,call',
                b'ret,push,pop,add',
                b'call,pop,mov,push',
                b'push,mov,ret,push',
                b'sub,ret,push,sub',
                b'add,call,mov,pop',
                b'ret,sub,call,push',
                b'call,push,sub,mov',
                b'mov,push,push,call',
                b'sub,mov,call,ret',
                b'add,call,pop,mov',
                b'call,add,add,sub',
                b'add,sub,call,sub',
                b'push,mov,add,ret',
                b'add,push,call,pop',
                b'sub,mov,sub,ret',
                b'pop,pop,pop,call',
                b'push,pop,call,ret',
                b'mov,call,add,pop']
    
    ###########################################################################
    
    @abstractmethod
    @feature('Byte Count')
    def byte_count(self):
        """Extract the number of bytes that are in the code section of the
        executable.
        
        This should not include addresses.
        
        Total number of features: 1
        """
        return self.byte_count()
        
    @abstractmethod
    @feature('Entropy')
    def entropy(self):
        """Extract the entropy of all of the bytes in the code section of the
        executable.
        
        Address bytes should not be included in the bytes used to calculate
        the entropy.
        
        Total number of features: 1
        """
        return self.entropy()
        
    @abstractmethod
    @feature('Entropy Stats')
    def entropy_stats(self):
        """Extract various statistics about the set of entropy values
        retrieved from the bytes in the code section of the executable. 
        
        The entropy values should be retrieved via the sliding window method
        using a window size of 10000. The addresses should not be included
        in the list of bytes.
        
        The following statistics should be retrieved from the distribution of
        entripy values and returned in a list (in the specified order):
        
            - Mean
            - Variance
            - Percentiles 0 - 100   
            
        Total number of features: 103
        """
        return self.entropy_stats()
    
    @abstractmethod
    @feature('First Address')
    def first_address(self):
        """Extract the address of the first code instruction in the executable
        binary.
        
        This should be formatted as a base 10 integer value.
        
        Total number of features: 1
        """
        return self.first_address()
        
    @abstractmethod
    @feature('Haralick Features')
    def haralick_features(self):
        """Extract the Haralick Features from an image constructed out of the
        grayscale pixels constructed from each of the hex digits in the code
        section of the executable.
        
        The features should be returned as a list.
        
        Total number of features: 52
        """
        return self.haralick_features()
        
    @abstractmethod
    @feature('Instruction Counts')
    def instruction_counts(self):
        """Extract the count of each of the instructions with the mnemonics
        that are returned by the static method instruction_list. 
        
        This should return a list of counts that corresponds with the values
        returned by instruction_list.
        
        Total number of features: 91
        """
        return self.instruction_counts()
    
    @abstractmethod
    @feature('Instruction Total')
    def instruction_total(self):
        """Extract the total number of the instructions that are returned 
        by the static method instruction_list.
        
        This should return a base-10 integer value.
        
        Total number of features: 1
        
        """
        return self.instruction_total()
        
    @abstractmethod
    @feature('Local Binary Patterns')
    def local_binary_patterns(self):
        """Extract the local binary pattern features from an image constructed
        out of the grayscale pixels constructed from each of the hex digits in
        the code section of the executable.
        
        Total number of features: 108
        """
        return self.local_binary_patterns()
    
    @abstractmethod
    @feature('1-Gram Frequencies')
    def one_gram_frequencies(self):
        """Extract the number of occurrences of all 256 possible bytes values
        (00 - FF) in the hex representation of the executable binary. This
        should not include any addresses.
        
        The return value should be a list of all of the frequencies in
        ascending order of the byte values they represent (starting with 00,
        ending with FF).
        
        Total number of features: 256
        """
        return self.one_gram_frequencies()
        
    @abstractmethod
    @feature('Registers')
    def register_counts(self):
        """Extract the count of register usages for each of the registers
        returned by the static register_list method.
        
        The returned value should be a list containing the counts
        corresponding to the list of registers.
        """
        return self.register_counts()
        
    @abstractmethod
    @feature('Section Sizes')
    def section_sizes(self):
        """Extract the size of each of the sections defined in the static
        section_list property.
        
        This should return a list of sizes that corresponds with the list of
        sections. Each size should be the number of bytes in the section.
        
        Total number of features: 9
        """
        return self.section_sizes()
        
    @abstractmethod
    @feature('String Lengths')
    def string_lengths(self):
        """Extract the numbers of strings in the code section of the executable
        that fit into various bins of string lengths. 
        
        The count of strings in the following bins should be returned in a
        list:
        
            (0, 10], 
            (10, 30], 
            (30, 60], 
            (60, 90], 
            (0, 100],
            (100, 150], 
            (150, 250], 
            (250, 400], 
            (400, 600], 
            (600, 900],
            (900, 1300],
            (1300, 2000], 
            (2000, 3000], 
            (3000, 6000], 
            (6000, 150000]
            (150000+)
            
        Total number of features: 16
        """
        return self.string_lengths()
    
    @abstractmethod
    @feature('Symbol Counts')
    def symbol_counts(self):
        """Extract the number of symbols in the op string.
        
        This should return a list of counts that corresponds with the list
        of symbols.
        
        Total number of features: 4
        """
        
        return self.symbol_counts()
        
    @abstractmethod
    #@feature('2-Gram Frequencies')
    def two_gram_frequencies(self):
        """Extract the number of occurrences of all 65,536 possible 2-gram
        values (0000 - FFFF) in the hex representation of the binary. This
        should not include any addresses.
        
        The return value shoud be a list of all of the frequencies in ascending
        order of the byte values they represent (starting with 0000, ending 
        with FFFF).
        
        Total number of features: 65,536
        """
        return self.two_gram_frequencies()
    
    @abstractmethod
    @feature('4-Gram Frequencies')
    def four_gram_frequencies(self):
        """Extract the number of occurrences of all 4,294,967,296 possible 
        2-gram values (00000000 - FFFFFFFF) in the hex representation of the 
        binary. This should not include any addresses.
        
        The return value shoud be a list of all of the frequencies in ascending
        order of the byte values they represent (starting with 00000000, ending 
        with FFFFFFFF).
        
        Total number of features: 4,294,967,296
        """
        return self.four_gram_frequencies()
