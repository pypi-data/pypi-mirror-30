import argparse
import sys
from . import resize, get_width

def resize_command():
    parser = argparse.ArgumentParser(prog="Resize", description='Resize and reformat any image or GIF.')
    parser.add_argument('--filename', '-f', type=str, metavar="filename", required=True, help='the name of the file to process')
    parser.add_argument('--output', '-o', type=str, metavar="output", required=True, help='the location of the output file')
    parser.add_argument('--width', '-w', type=int, metavar="width", help='the new width', default=None)
    parser.add_argument('--height', type=int, metavar="height", help='the new height', default=None)

    args = parser.parse_args()
    
    result = resize(args.filename, args.output, args.width, args.height)

    if not result:
        print("Something went wrong...")
        sys.exit()
    print("Done!")

def size_command():
    parser = argparse.ArgumentParser(prog="Get Size", description='Get the size of any image.')
    parser.add_argument('--filename', '-f', type=str, metavar="filename", required=True, help='the name of the file to check')

    args = parser.parse_args()
    result = get_width(args.filename)
    if not result:
        print("Something went wrong, does the file exist?")
        sys.exit()
    print("This file's size is {}x{}".format(*result))