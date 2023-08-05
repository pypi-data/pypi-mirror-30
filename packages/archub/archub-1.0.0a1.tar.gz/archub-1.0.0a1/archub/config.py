import os

def assert_get_environ(envname):
    value = os.environ.get(envname)
    assert value is not None, 'Environment variable {} is not defined'.format(envname)
    return value

GITHUB_TOKEN = assert_get_environ('GITHUB_TOKEN')
GITHUB_ORGANIZATION = assert_get_environ('GITHUB_ORGANIZATION')
