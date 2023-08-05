import os
import sys
from argparse import ArgumentParser
from archub import cmdline, config
from github import Github
from archub.core import print_issues, print_issues_with_labels

def main(args):
    parser = ArgumentParser(
        prog=cmdline.prog(__file__),
        description='List assigned issues'
    )
    parser.add_argument('-l', '--labels',
        help='include labels in output', default=False, action='store_true')
    parsed_args = parser.parse_args(args)
    if parsed_args.labels:
        print_issues_with_labels()
    else:
        print_issues()
    return 0

if '__main__' == __name__:
    sys.exit(main(sys.argv))
