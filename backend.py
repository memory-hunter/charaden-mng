import struct

IN_PHONE_PATH = 'home/moapl/userdata/avatar/'
AVATAR_MNG_PATH: str = ''
AVATAR_MNG_SZ: int = 6564
LAST_INDEX: int = -1

'''
AVATAR.MNG specification:

encoding - shift-jis
endianness - little
file size from system - 6564 bytes (not sure if extensible)
each charaden page size - 0x290 (656 bytes)
limit - 10(?) - (6564/656 =~ 10)

valid page:
0x0 - index - int32 - starts from 1
0x6 - name - shift-jis string - length???
0x48 - title - shift-jis string - length???
0x178 - size of file - int32
0x17C - path - valid path string - length???
0x158 - width - int32
0x15C - height - int32

empty page:
FF FF FF FF and 00 bytes for the rest of 0x290
'''

class Charaden:
    def __init__(self, name: str, title: str, size_of_file: int, path: str, width: int, height: int):
        self.name = name
        self.title = title
        self.size_of_file = size_of_file
        self.path = path
        self.width = width
        self.height = height

    def __repr__(self):
        return (f"Name: {self.name}\nTitle: {self.title}\nSize: {self.size_of_file}"
                f"\nWidth: {self.width}\nHeight: {self.height}")

CHARADEN_LIST: list[Charaden] = []
change_made = False

def check_last_index():
    with open(AVATAR_MNG_PATH, 'rb', encoding='shift-jis') as avmng:
        last_idx = 0
        while True:
            idx = avmng.read(0x4)
            if idx == '':
                LAST_INDEX = last_idx
                return
            idx = int(idx)
            if int(idx) != 0xFFFFFFFF:
                last_idx = max(last_idx, idx)
            avmng.read(0x28C)

def read_list():
    with open(AVATAR_MNG_PATH, 'rb') as file:
        for i in range(10):
            offset = i * 0x290
            file.seek(offset)

    
            index_bytes = file.read(4)
            index = struct.unpack('<I', index_bytes)[0]
    
            if index == 0xFFFFFFFF:
                continue

            file.seek(offset + 0x6)
            name_bytes = bytearray()
            while True:
                char = file.read(1)
                if char == b'\x00' or not char:
                    break
                name_bytes += char
            name = name_bytes.decode('shift-jis')

    
            file.seek(offset + 0x48)
            title_bytes = bytearray()
            while True:
                char = file.read(1)
                if char == b'\x00' or not char:
                    break
                title_bytes += char
            title = title_bytes.decode('shift-jis')

    
            file.seek(offset + 0x178)
            size_of_file_bytes = file.read(4)
            size_of_file = struct.unpack('<I', size_of_file_bytes)[0]

    
            file.seek(offset + 0x17C)
            path_bytes = bytearray()
            while True:
                char = file.read(1)
                if char == b'\x00' or not char:
                    break
                path_bytes += char
            path = path_bytes.decode('shift-jis')

    
            file.seek(offset + 0x158)
            width_bytes = file.read(4)
            width = struct.unpack('<I', width_bytes)[0]

    
            file.seek(offset + 0x15C)
            height_bytes = file.read(4)
            height = struct.unpack('<I', height_bytes)[0]

    
            CHARADEN_LIST.append(Charaden(name, title, size_of_file, path, width, height))

def print_list():
    for i, chrdn in enumerate(CHARADEN_LIST):
        if i == len(CHARADEN_LIST) - 1: print()
        print(str(i + 1) + ":\n" + repr(chrdn))

def insert():
    # Take in all data and add to list
    global change_made
    change_made = True
    check_last_index()

def delete(index: int):
    # Delete with an index
    global change_made
    change_made = True
    CHARADEN_LIST.pop(index - 1)