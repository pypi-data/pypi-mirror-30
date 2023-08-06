import os
import sys
from argparse import ArgumentParser
from archub import cmdline, config
from archub.core import branch

def main(args):
    parser = ArgumentParser(
        prog=cmdline.prog(__file__),
        description='Switch to repository branch'
    )
    parser.add_argument('issue',
        help='Issue number or custom branch name')
    parsed_args = parser.parse_args(args)
    try:
        branch(parsed_args.issue)
    except Exception as e:
        print(str(e))
    return 0

if '__main__' == __name__:
    sys.exit(main(sys.argv))
