import os
from github import Github

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)
ORGANIZATION = os.environ.get('GITHUB_ORGANIZATION', None)


class GithubRepository(object):
    def __init__(self, repo_name):
        self.github = Github(GITHUB_TOKEN)
        self.org = self.github.get_organization(ORGANIZATION)
        self.repo = self.org.get_repo(repo_name)

    def create_issue(self, *args, **kwargs):
        return self.repo.create_issue(*args, **kwargs)


class GithubOrganization(object):
    pass


class GithubUser(object):
    pass
