import os
import sys

def prog(filepath):
    return '{} {}'.format(os.path.basename(sys.argv[0]), os.path.basename(filepath)[:-3])
