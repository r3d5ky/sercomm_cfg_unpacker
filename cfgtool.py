"""
Copyright (c) 2022 r3d5ky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""

import zlib
import sys
import argparse

def unpack(cfg_file, raw):
    with open(cfg_file, 'rb') as f:
        infile = f.read()

    unpacked = zlib.decompress(infile[4:])
    config = unpacked[unpacked.find(b'\x3c\x44\x41\x54\x41'):-6]
    userdata = unpacked[:unpacked.find(b'\x3c\x44\x41\x54\x41')]
    
    if raw:
        with open(cfg_file[:-4] + '_raw.txt', 'wb') as f:
            f.write(unpacked)

    with open(cfg_file[:-4] + '.xml', 'wb') as f:
        f.write(config)
    with open(cfg_file[:-4] + '_userdata.bin', 'wb') as f:
        f.write(userdata)


def pack(xml_file, endianness):
    with open(xml_file, 'rb') as f:
        rawconfig = f.read() + b'\x0a\x00'
    with open(xml_file[:-4] + '_userdata.bin', 'rb') as f:
        userdata = f.read()
    endian = "little"
    if endianness:
        endian = "big"
    crc = zlib.crc32(rawconfig).to_bytes(4, endian)
    config = userdata + rawconfig + crc
    
    with open(sys.argv[2][:-4] + '_changed.cfg', 'wb') as f: 
        f.write(len(config).to_bytes(4, endian) + zlib.compress(config))


def main():
    parser = argparse.ArgumentParser(description="Sercomm backup config packer/unpacker")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u","--unpack", action='store_true', help="unpack .cfg file to .xml + header")
    group.add_argument("-p","--pack", action='store_true', help="pack .xml + header back to .cfg")
    parser.add_argument("-r","--raw", action='store_true', help="create additional file with raw unpacked data (optional)")
    parser.add_argument("-b","--big", action='store_true', help="pack for Big Endian arch (default is Little Endian)")
    parser.add_argument('file', type=str, help="path to .cfg/.xml file for unpacking/packing")
    args = parser.parse_args()
    
    if args.unpack:
        unpack(args.file, args.raw)
    elif args.pack:
        pack(args.file, args.be)

    print("Done!")


if __name__ == '__main__':
    main()