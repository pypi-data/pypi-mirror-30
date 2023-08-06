import os
import re
from git import Repo

def assert_get_environ(envname):
    value = os.environ.get(envname)
    assert value is not None, 'Environment variable {} is not defined'.format(envname)
    return value

GITHUB_TOKEN = assert_get_environ('GITHUB_TOKEN')

def find_repo():
    current_directory = os.getcwd()
    while current_directory != os.path.sep:
        try:
            r = Repo(current_directory)
            return r
        except Exception:
            current_directory = os.path.realpath(os.path.join(current_directory, '..'))
    raise Exception('Could not find a git repository')

try:
    repo = find_repo()
except Exception:
    repo = None

def organization_from_remote_url(url):
    return url.split(':')[1].split('/', 1)[0]

def repository_from_remote_url(url):
    return url.split(':')[1].split('/', 1)[1].rsplit('.', 1)[0]

def org_and_reponame_from_repo(r):
    if r is None:
        return None, None
    for url in r.remote('origin').urls:
        if url.startswith('git@github.com:'):
            return organization_from_remote_url(url), repository_from_remote_url(url)
    return None, None

GITHUB_ORGANIZATION, GITHUB_REPOSITORY_NAME = org_and_reponame_from_repo(repo)

def issue_number_from_repo(r):
    if r is None:
        return None
    regex = re.compile('^(\d+)-')
    match = regex.match(r.active_branch.name)
    if match is not None:
        issuenum = int(match.groups()[0])
        return issuenum
    return None

GITHUB_ISSUE_NUMBER = issue_number_from_repo(repo)

try:
    from termios import TIOCGWINSZ
    from fcntl import ioctl
    from struct import unpack
    from sys import stdout
    TTY_ROWS, TTY_COLS = unpack('HH', ioctl(stdout.fileno(), TIOCGWINSZ, '    '))
except Exception as e:
    TTY_ROWS, TTY_COLS = 25, 80
