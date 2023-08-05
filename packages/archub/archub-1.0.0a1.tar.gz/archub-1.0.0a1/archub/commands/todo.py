import os
import sys
from argparse import ArgumentParser
from archub import cmdline, config
from archub.core import todo
from github import Github

def get_repo(github, org, repo_name):
    if len(org) > 0:
        return github.get_organization(org).get_repo(repo_name)
    return github.get_user().get_repo(repo_name)

def main(args):
    parser = ArgumentParser(
        prog=cmdline.prog(__file__),
        description='Quickly create an issue ticket for the specified repository'
    )
    parser.add_argument('-o', '--org', required=False, type=str, default=None)
    parser.add_argument('-r', '--repo', required=True, type=str)
    parser.add_argument('-t', '--title', required=False, type=str, default=None)
    parser.add_argument('-a', '--assign', required=False, type=str, default=None,
        help='To whom this issue will be assigned [default: self]')
    parser.add_argument('body')
    parsed_args = parser.parse_args(args)
    todo(
        parsed_args.org,
        parsed_args.repo,
        parsed_args.title,
        parsed_args.body,
        parsed_args.assign
    )
    return 0

if '__main__' == __name__:
    sys.exit(main(sys.argv))
