import sys
from archub import config
from github import Github

def main(args):
    try:
        gh = Github(config.GITHUB_TOKEN)
        r = gh.get_repo('{}/{}'.format(config.GITHUB_ORGANIZATION, config.GITHUB_REPOSITORY_NAME))
        issue_numbers = [i.number for i in r.get_issues()]
        print(' '.join(list(map(lambda x: str(x), issue_numbers))))
    except Exception as e:
        pass
    return 0

if '__main__' == __name__:
    sys.exit(main())
