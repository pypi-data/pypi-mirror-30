#!/usr/bin/env python3
# © 2016 James R. Barlow: github.com/jbarlow83
import sys
import os
import signal


VERSION_STRING = '''tesseract 3.05.01
 leptonica-1.74.4
  libjpeg 9b : libpng 1.6.32 : libtiff 4.0.8 : zlib 1.2.8
SPOOFED: CRASH ON OCR or -psm 0
'''

"""Simulates a Tesseract crash when asked to run OCR

It isn't strictly necessary to crash the process and that has unwanted
side effects like triggering core dumps or error reporting, logging and such.
It's enough to dump some text to stderr and return an error code.

Follows the POSIX(?) convention of returning 128 + signal number.

"""


def main():
    if sys.argv[1] == '--version':
        print(VERSION_STRING, file=sys.stderr)
        sys.exit(0)
    elif sys.argv[1] == '--list-langs':
        print('List of available languages (1):\neng', file=sys.stderr)
        sys.exit(0)
    elif sys.argv[1] == '--print-parameters':
        print('A parameter list would go here\ntextonly_pdf 0\n',
              file=sys.stderr)
        sys.exit(0)
    elif sys.argv[-2] == 'hocr':
        print("KABOOM! Tesseract failed for some reason", file=sys.stderr)
        sys.exit(128 + signal.SIGSEGV)
    elif sys.argv[-2] == 'pdf':
        print("KABOOM! Tesseract failed for some reason", file=sys.stderr)
        sys.exit(128 + signal.SIGSEGV)
    elif sys.argv[-1] == 'stdout':
        print("libc++abi.dylib: terminating with uncaught exception of type "
              "std::bad_alloc: std::bad_alloc", file=sys.stderr)
        sys.exit(128 + signal.SIGABRT)
    else:
        print("Spoof doesn't understand arguments", file=sys.stderr)
        print(sys.argv, file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
