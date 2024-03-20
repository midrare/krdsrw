#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import sys

from . import cursor
from . import objects


def main(argv: None | list[str] = None) -> int:
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description='Parse Kindle datastore files')
    parser.add_argument(
        '-i',
        '--in-file',
        metavar='FILE',
        type=argparse.FileType('rb'),
        help='file path to read',
        required=True)

    parser.add_argument(
        '-o',
        '--out-file',
        metavar='FILE',
        type=argparse.FileType('wb'),
        help='file path to write',
        required=False)

    args = parser.parse_args(argv[1:])
    if args.in_file:
        csr = cursor.Cursor()
        csr.load(args.in_file.read())

        root = objects.DataStore()
        root.read(csr)

        ser = json.dumps(root, default=lambda o: o.__json__(), indent=2)

        if args.out_file and args.out_file.name != "-":
            args.out_file.write(ser.encode("utf-8"))
        else:
            print(ser)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
