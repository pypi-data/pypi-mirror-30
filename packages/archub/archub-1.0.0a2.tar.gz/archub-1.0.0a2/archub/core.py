from github import Github
from github.GithubObject import NotSet
from archub import config

def todo(org, repo, title, body, assignee):
    g = Github(config.GITHUB_TOKEN)
    login = g.get_user().login
    if assignee is None:
        assignee = login
    if org is None:
        org = login
    org_repo = '{}/{}'.format(org, repo)
    if title is None:
        title = body
        body = NotSet
    r = g.get_repo(org_repo)
    r.create_issue(
        title,
        body=body,
        assignee=assignee
    )
