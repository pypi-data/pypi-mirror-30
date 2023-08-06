import os
import sys
from argparse import ArgumentParser
from archub import cmdline, config
from github import Github
from archub.core import print_issues, print_issues_with_labels

def main(args):
    show_all_default = config.GITHUB_REPOSITORY_NAME is None
    parser = ArgumentParser(
        prog=cmdline.prog(__file__),
        description='List all assigned issues' if show_all_default else
            'List assigned issues for {}/{}'\
            .format(
                config.GITHUB_ORGANIZATION,
                config.GITHUB_REPOSITORY_NAME)
    )
    parser.add_argument('-l', '--labels',
        help='include labels in output', default=False,
        action='store_true')
    parser.add_argument('-a', '--all',
        default=show_all_default,
        action='store_true',
        help='show all assigned issues [default: True]' if show_all_default else
            'show all assigned issues, not just issues for {}/{} [default: False]'\
                .format(config.GITHUB_ORGANIZATION, config.GITHUB_REPOSITORY_NAME))
    parser.add_argument('-w', '--wide', default=False,
        action='store_true', help='use the full width of the terminal')
    parsed_args = parser.parse_args(args)
    linewidth = config.TTY_COLS if parsed_args.wide else 80
    if parsed_args.labels:
        print_issues_with_labels(parsed_args.all, linewidth=linewidth)
    else:
        print_issues(parsed_args.all, linewidth=linewidth)
    return 0

if '__main__' == __name__:
    sys.exit(main(sys.argv))
