import os
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
