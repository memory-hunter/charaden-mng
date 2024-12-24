import os
from pathlib import Path
import struct

IN_PHONE_PATH = '/home/moapl/userdata/avatar/'
AVATAR_MNG_PATH: str = ''
AVATAR_MNG_SZ: int = 6564

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
0x48 - 0x90 - title - shift-jis string - max.length of 36 bytes.
0x158 - width - int32
0x15C - height - int32
0x178 - size of file - int32
0x17C - path - valid path string - length???

everything else is surrounded by null bytes

empty page:
FF FF FF FF and 00 bytes for the rest of 0x290
'''

class Charaden:
    def __init__(self, name: bytes, title: bytes, size_of_file: int, path_pc: str, path_phone, width: int, height: int):
        self.name = name
        self.title = title
        self.size_of_file = size_of_file
        self.path_pc = path_pc
        self.path_phone = path_phone
        self.width = width
        self.height = height

    def __repr__(self):
        return (f"Name: {self.name.decode("shift-jis")}\n"
                f"Title: {self.title.decode("shift-jis")}\n"
                f"Size: {self.size_of_file}\n"
                f"Path: {self.path_phone}\n"
                f"Width: {self.width}\n"
                f"Height: {self.height}")


CHARADEN_LIST: list[Charaden] = []
change_made = False

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
            name = name_bytes

    
            file.seek(offset + 0x48)
            title_bytes = bytearray()
            while True:
                char = file.read(1)
                if char == b'\x00' or not char:
                    break
                title_bytes += char
            title = title_bytes

    
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
            path = path_bytes.decode()

    
            file.seek(offset + 0x158)
            width_bytes = file.read(4)
            width = struct.unpack('<I', width_bytes)[0]

    
            file.seek(offset + 0x15C)
            height_bytes = file.read(4)
            height = struct.unpack('<I', height_bytes)[0]

    
            CHARADEN_LIST.append(Charaden(name, title, size_of_file, '', path, width, height))

def print_list():
    if len(CHARADEN_LIST) == 0:
        print("List of Chara-dens is empty.")
        return
    for i, chrdn in enumerate(CHARADEN_LIST):
        if i == len(CHARADEN_LIST) - 1: print()
        print(str(i + 1) + ":\n" + repr(chrdn))

def insert(charaden: Charaden):
    global change_made
    change_made = True
    CHARADEN_LIST.append(charaden)

def delete(index: int):
    global change_made
    change_made = True
    CHARADEN_LIST.pop(index - 1)

def charaden_page(charaden: Charaden, idx: int) -> bytes:
    name_max_length = 0x48 - 0x6
    title_max_length = 0x158 - 0x48
    path_max_length = 0x290 - 0x17C

    name_encoded = charaden.name[:name_max_length]
    title_encoded = charaden.title[:title_max_length]
    
    if charaden.path_pc != '':
        path_parts = charaden.path_pc.split(os.sep)
        path_parts = list(map(lambda part: os.sep if part == '' else part, charaden.path_pc.split(os.sep)))
        directory_parts = path_parts[:-1]
        new_filename = f"{str(idx).zfill(2)}.AFD"
        new_path = Path(os.path.join(*directory_parts, new_filename)).as_posix()
        try:
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            old_path_pc = charaden.path_pc
            if old_path_pc != new_path:
                os.rename(old_path_pc, new_path)
                print(f"File renamed from {old_path_pc} to {new_path} for phone compatibility.")
        except Exception as e:
            print(f"Error renaming file. Reason: {e}. Exiting...")
            exit()
        path_encoded = new_path[:path_max_length].encode('shift-jis')
    else:
        path_encoded = charaden.path_phone[:path_max_length].encode('shift-jis')
    name_padded = name_encoded.ljust(name_max_length, b'\x00')
    title_padded = title_encoded.ljust(title_max_length, b'\x00')
    path_padded = path_encoded.ljust(path_max_length, b'\x00')

    page = struct.pack(
        '<I', idx
    ) + b'\x00\x00'

    page += name_padded
    page += title_padded

    page += struct.pack(
        '<I', charaden.width
    ) + struct.pack(
        '<I', charaden.height
    )
    
    page += b'\x00' * (0x178 - 0x160)

    page += struct.pack(
        '<I', charaden.size_of_file
    )

    page += path_padded

    page_padded = page.ljust(0x290, b'\x00')

    return page_padded


def empty_charaden_page() -> bytes:
    return b'\xFF\xFF\xFF\xFF' + b'\x00' * (0x290 - 0x4)

def write_avatar_mng_file():
    buffer = bytes()
    for i in range(10):
        if i >= len(CHARADEN_LIST):
            buffer += empty_charaden_page()
        else:
            buffer += (charaden_page(CHARADEN_LIST[i], i + 1))
    buffer += (b'\x01\x00\x00\x00')
    with open(AVATAR_MNG_PATH, 'wb') as avmng:
        avmng.write(buffer)