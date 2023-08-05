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

def get_issues():
    return Github(config.GITHUB_TOKEN).get_user().get_issues()

def print_issues():
    for issue in get_issues():
        print_issue_line(issue)

def print_issues_with_labels():
    for issue in get_issues():
        print_issue_line(issue)
        if len(issue.labels) > 0:
            print_issue_labels(issue)

def issue_title_to_branchname(title):
    reduced = ''.join([c if c not in string.punctuation else '' for c in title])
    return ''.join([c if c in string.ascii_letters + string.digits else '-' for c in reduced])

def resolve_issuenum_to_branchname(repo, issuenum):
    gh = Github(config.GITHUB_TOKEN)
    return '{}-{}'.format(
        issuenum,
        issue_title_to_branchname(
            gh.get_user().get_repo(repo).get_issue(issuenum).title
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
            branchname = resolve_issuenum_to_branchname(config.GITHUB_REPOSITORY_NAME, issuenum)
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
