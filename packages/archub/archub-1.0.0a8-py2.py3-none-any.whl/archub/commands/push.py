import os
import sys
from argparse import ArgumentParser
from archub import cmdline, config
from archub.core import push

def main(args):
    assert config.repo is not None, 'This command must be run from within a git repository.'
    assert config.repo.active_branch != 'master', 'Will not push to remote master; use git.'
    parser = ArgumentParser(
        prog=cmdline.prog(__file__),
        description='Create a remote branch and set current local branch [{}] to track the remote branch.'\
          .format(config.repo.active_branch.name)
    )
    parsed_args = parser.parse_args(args)
    try:
        push()
    except Exception as e:
        print(str(e))
    return 0

if '__main__' == __name__:
    sys.exit(main(sys.argv))
