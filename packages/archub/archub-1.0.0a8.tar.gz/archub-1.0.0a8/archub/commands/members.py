import sys
from archub import config
from github import Github

def main(args):
    try:
        gh = Github(config.GITHUB_TOKEN)
        o = gh.get_organization(config.GITHUB_ORGANIZATION)
        members = [m.login for m in o.get_members()]
        print(' '.join(members))
    except Exception:
        pass
    return 0

if '__main__' == __name__:
    sys.exit(main())
