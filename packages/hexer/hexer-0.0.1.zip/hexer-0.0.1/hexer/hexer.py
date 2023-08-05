# -*- coding: utf-8 -*-

### imports ###################################################################        
import logging
import struct
import yaml

###############################################################################        
def create_block_config(blocks, **kwargs):
    block_list = []
    filename = ''

    for key, value in kwargs.items():
        if key == 'filename':
            filename = value
    
    if filename:
        with open(filename, 'w') as f:
            yaml.dump(blocks, f)
    else:
        block_list = yaml.dump(blocks)

    # yaml.safe_dump(blocks, f)
    return block_list

###############################################################################        
def read_block_config(filename):
    blocks = []
    
    with open(filename, 'r') as f:
        blocks = yaml.load(f)

    return blocks

###############################################################################
class Block:
    def __init__(self, buffer, **kwargs):
        self.buffer = buffer
        self.chunk_dict = {}
        self.block_dict = {}
        self.fmt = ''
        self.values = []
        
        for key, value in kwargs.items():
            if key == 'block_dict':
                self.block_dict = value
            elif key == 'chunk_dict':
                self.chunk_dict = value
            elif key == 'fmt':
                self.fmt = value

    def readBuffer(self):
        if self.block_dict:
            
            offset = 0
            size = len(self.buffer)

            print()
            
            while offset < size:
                buffer = self.buffer[offset:size]
                
                chunk = Chunk(buffer, chunk_dict=self.chunk_dict)
                chunk_size = chunk.readBuffer()
            
            
        elif self.chunk_dict:
            offset = 0
            size = len(self.buffer)

            print()
            
            while offset < size:
                buffer = self.buffer[offset:size]
                
                chunk = Chunk(buffer, chunk_dict=self.chunk_dict)
                chunk_size = chunk.readBuffer()
                
                if not chunk_size:
                    break
        
                offset += chunk_size
        
                print(offset, chunk.data_dict)                
            
        elif self.fmt:
            self.values = struct.unpack_from(self.fmt, self.buffer)
            
        return self.values

###############################################################################
class Chunk:
    def __init__(self, buffer, **kwargs):
        self.buffer = buffer
        
        for key, value in kwargs.items():
            if key == 'chunk_dict':
                for k, v in value.items():
                    print(k, v)
                    setattr(self, k, v)
        
        self.terminator_size = len(self.terminator)

        self.data_dict = {}

    def check_for_terminator(self):
        i2 = self.terminator_size
        
        result = False
        
        if self.buffer[:i2].decode("utf-8") == self.terminator:
            print('Terminator is out there!')
            result = True
            
        return result
        
    def readBuffer(self):

        if self.check_for_terminator():
            return 0
        
        for name, offset, size, dtype in self.structure:

            ## evaluate variables
            if type(size) == str:
                size = eval(size)
                
            if dtype not in ('utf-8', '<d', '<i', '<H'):
                dtype = eval(dtype)

            i1 = offset
            i2 = offset + size

            if dtype == 'utf-8':
                value = self.buffer[i1:i2].decode("utf-8").rstrip('\x00')
            elif dtype in ('<d', '<i', '<H'):
                value = struct.unpack(dtype, self.buffer[i1:i2])[0]
                
            self.data_dict[name] = value
            setattr(self, name, value)

            # print(name, value, dtype, size, i1, i2)

        return i2        
        
###############################################################################
class Hexer:
    def __init__(self, filename, **kwargs):
        self.blocks = []
        self.data_dict = {}
        self.name = ''
        
        for key, value in kwargs.items():
            if key == 'blocks':
                self.blocks = value
            elif key == 'config_file':
                self.blocks = read_block_config(value)
            elif key == 'name':
                self.name = value
        
        with open(filename, 'rb') as f:
            self.data = f.read()
            
        self.Nbytes = len(self.data)

    def evaluate(self, source):
        return eval(source)
        
    def readBlocks(self):
        self.offset = 0
        
        for block_dict in self.blocks:
            block = HeaderBlock(self, block_dict=block_dict)
            values = block.readBlock()
            self.data_dict[block.name] = values
            
            if block.name not in self.__dict__.keys():
                setattr(self, block.name, block)
                
            self.offset += block.size

        
    def hexdump(self, **kwargs):
        do_print = True
        offset_0 = 0
        offset_1 = 0
        size = 0
        
        for key, value in kwargs.items():
            if key == 'offset':
                offset_0 = value
            elif key == 'output':
                do_print = False
            elif key == 'size':
                size = value

        # dump from tail
        if offset_0 < 0:
            offset_1 = self.Nbytes + offset_0 + 1
            # print('offset_1', offset_1)
                
        if not size:
            size = self.Nbytes - offset_0

        if offset_1:
            # dump from tail
            offset_0 = offset_1 - size
        else:
            offset_1 = offset_0 + size

        prev_data_str = ''

        # print(offset_0, size, offset_1)

        if do_print:
            print()
        
        for offset in range(offset_0, offset_1, 16):
            i1 = min((offset + 16, offset_1))

            chunk = self.data[offset:i1]
            text = chunk.decode('ascii', errors='replace')

            text = ''.join(
                    [c if ord(c) < 128 and ord(c) > 32 else '.' for c in text])

            offset_str = "{:06d}".format(offset)

            data_str = " ".join("{:02X}".format(c) for c in chunk[:8]) + '  '
            data_str += " ".join("{:02X}".format(c) for c in chunk[8:])

            if data_str != prev_data_str:
                output = "  ".join([offset_str, data_str, text])
            else:
                output = '*'

            if do_print:
                print(output)
                
            prev_data_str = data_str

    def strings(self, **kwargs):
        
        chars = []
        strings = []
        offsets = []
        
        min_len = 4

        for key, value in kwargs.items():
            if key == 'min_len':
                min_len = value
        
        for i in range(self.Nbytes):
            byte = self.data[i]
            
            if byte >= 32 and byte < 127:
                if not chars:
                    offset = i
                
                char = struct.unpack('<1c', self.data[i:i+1])[0].decode()
                chars.append(char)
            else:
                if len(chars) >= min_len:
                    s = ''.join(chars)
                    strings.append(s)
                    offsets.append(offset)
                    
                chars = []
            
        return offsets, strings

###############################################################################
class HeaderBlock:
    def __init__(self, parent, block_dict):
        self.dtype = ''
        self.fmt = tuple([])
        self.length = 0
        self.offset = 0
        self.parent = parent
        self.size = 0
        self.structure = tuple([])
        self.value_dict = {}
        
        for key, value in block_dict.items():
            setattr(self, key, value)

        if not self.offset:
            self.offset = self.parent.offset

        if self.length and self.dtype:
            if type(self.length) == str:
                self.length = self.parent.evaluate(self.length)
                
            self.fmt = '<' + str(self.length) + self.dtype
            
        if not self.structure:
            self.structure = ((0, self.name, self.fmt),)

        if not self.size:
            last_offset, name, fmt = self.structure[-1]
            self.size = last_offset + struct.calcsize(fmt)
            
        self.buffer = self.parent.data[self.offset:self.offset+self.size]

    def readBlock(self):
        for offset, name, fmt in self.structure:
            values = struct.unpack_from(fmt, self.buffer[offset:])

            if len(values) == 1:
                values = values[0]
                
            self.value_dict[name] = values
            
            if name not in self.__dict__.keys():
                setattr(self, name, values)

        if len(self.structure) == 1:
            self.values = values

        return self.value_dict