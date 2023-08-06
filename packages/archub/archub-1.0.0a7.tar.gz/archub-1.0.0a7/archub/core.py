from git import RemoteReference
import string
from github import Github
from github.GithubObject import NotSet
from github.GithubException import UnknownObjectException
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

def render_fixed_width_text(text, maxlen=80):
    if len(text) > maxlen:
        return '{}...'.format(text[:maxlen - 3])
    return text + ' ' * (maxlen - len(text))

def render_issue_line(issue, linewidth=80):
    return '{} {} {}'.format(
        render_fixed_width_text('#% 4d' % issue.number, 5),
        render_fixed_width_text(issue.title, linewidth - (24 + 5 + 2)),
        render_fixed_width_text(issue.repository.name, 24)
    )

def render_issue_labels(issue, linewidth=80):
    return render_fixed_width_text(' '.join(['[{}]'.format(label.name) for label in issue.get_labels()]), linewidth)

def print_issue_line(issue, linewidth=80):
    print(render_issue_line(issue, linewidth))

def print_issue_labels(issue, linewidth=80):
    pad = '      '
    print(pad + render_issue_labels(issue, linewidth - len(pad)))

def get_issues(get_all_issues):
    gh = Github(config.GITHUB_TOKEN)
    user = gh.get_user()
    issues = user.get_issues()
    if get_all_issues:
        return issues
    else:
        # yes, this seems obtuse, but directly querying the
        # requested repository for assigned issues is SLOW
        return filter(
            lambda x: x.repository.name == config.GITHUB_REPOSITORY_NAME,
            issues)

def print_issues(show_all=True):
    for issue in get_issues(show_all):
        print_issue_line(issue)

def print_issues_with_labels(show_all=True):
    for issue in get_issues(show_all):
        print_issue_line(issue)
        if len(issue.labels) > 0:
            print_issue_labels(issue)

def issue_title_to_branchname(title):
    reduced = ''.join([c if c not in string.punctuation else '' for c in title])
    return ''.join([c if c in string.ascii_letters + string.digits else '-' for c in reduced])

def resolve_issuenum_to_branchname(org, repo, issuenum):
    gh = Github(config.GITHUB_TOKEN)
    return '{}-{}'.format(
        issuenum,
        issue_title_to_branchname(
            gh.get_repo('{}/{}'.format(org,repo)).get_issue(issuenum).title
        )
    )

def branch(issuenum_or_branchname):
    current_repo = config.find_repo()
    if current_repo is None:
        raise RuntimeError('Not inside a git repository')
    try:
        issuenum = int(issuenum_or_branchname)
    except ValueError:
        issuenum = None
    if issuenum is not None:
        try:
            branchname = resolve_issuenum_to_branchname(
                config.GITHUB_ORGANIZATION,
                config.GITHUB_REPOSITORY_NAME,
                issuenum)
        except UnknownObjectException:
            raise RuntimeError('Unknown issue number {}'.format(issuenum))
    else:
        branchname = issuenum_or_branchname
    if current_repo.active_branch.name == branchname:
        # do nothing, we're already on the desired branch
        print('Already on desired branch, doing nothing.')
        return
    if current_repo.is_dirty():
        raise RuntimeError('Current branch is dirty, commit your changes before creating a new branch.')
    for branch in current_repo.branches:
        if branch.name == branchname:
            branch.checkout()
            print('Checked out already existing branch: {}'.format(branch.name))
            return
    new_head = current_repo.create_head(branchname)
    new_head.checkout()
    print('Created new branch: {}'.format(branchname))


def pullrequest(title, body='', base='master', maintainer_can_modify=True):
    repo = config.repo
    assert repo.is_dirty() is False, 'Your branch is dirty; commit your changes and try again.'
    remote = repo.remote()
    assert remote.exists(), 'Repository remote doesn\'t exist; aborting.'
    # push the current branch to origin as a remote branch (if it doesn't already exist)
    ret = remote.push('refs/heads/{0}:refs/heads/{0}'.format(repo.active_branch.name))
    repo.active_branch.set_tracking_branch(
        RemoteReference(
            repo,
            'refs/remotes/origin/{}'.format(repo.active_branch.name)
        )
    )
    gh = Github(config.GITHUB_TOKEN)
    github_repo = gh.get_repo('{}/{}'.format(config.GITHUB_ORGANIZATION, config.GITHUB_REPOSITORY_NAME))
    # look up the issue if our branch name is prefixed with r/\d+-/
    if config.GITHUB_ISSUE_NUMBER is not None:
        issue = github_repo.get_issue(config.GITHUB_ISSUE_NUMBER)
    else:
        issue = None
    if issue is None:
        github_repo.create_pull(
            title,
            body,
            base,
            repo.active_branch.name,
            maintainer_can_modify=maintainer_can_modify)
    else:
        try:
            pr = github_repo.get_pull(config.GITHUB_ISSUE_NUMBER)
            if 'closed' == pr.state:
                pr.edit(state='open')
            return
        except Exception:
            # pull request already exists, do nothing
            return
        github_repo.create_pull(
            issue,
            base,
            repo.active_branch.name)
