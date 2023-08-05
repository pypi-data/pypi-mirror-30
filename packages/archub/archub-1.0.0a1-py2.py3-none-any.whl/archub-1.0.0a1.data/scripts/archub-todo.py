import os
import sys
from argparse import ArgumentParser
from archub import cmdline

def main():
    parser = ArgumentParser(prog=cmdline.arg_zero(sys.argv[0]))
    args = parser.parse_args()
    return 0

if '__main__' == __name__:
    sys.exit(main())
