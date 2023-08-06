import re

from sys import argv, stderr, exit
from shell_helper.bases import run_cmd, split_line
from shell_helper.cvs.git import git, get_remote_list, GitRemoteEntry


GIT_EXTENSION = '.git'
REGEX_GITHUB_REMOTE = re.compile(
    r'^[\w-]+((://)|@)(w{3}\.)?github.com[:/]'
    r'(?P<USER>[^/]+)/(?P<REPO>[^$]+)$', re.I | re.U)


def get_current_branch():
    response = git.run('branch', '-v', strict=True).stdout.decode('utf-8').strip()
    if not response:
        raise RuntimeError('There is no active branch. Please push to remote first.')
    current_branch = split_line(response)[1]
    return current_branch


def parse_remote_as_github_url(remote: GitRemoteEntry):
    m = REGEX_GITHUB_REMOTE.match(remote.url)
    if m is not None:
        organization = m.group('USER')
        repository = m.group('REPO')
        if repository.endswith(GIT_EXTENSION):
            repository = repository[:-len(GIT_EXTENSION)]
        return 'https://github.com/{}/{}'.format(organization, repository)
    raise RuntimeError('{.url} is not a valid GitHub repository URL'.format(remote))


def blame(relative_path, line, remote='origin', branch=None):
    base_url = None

    for remote_item in get_remote_list():  # type: GitRemoteEntry
        if remote_item.remote == remote:
            base_url = parse_remote_as_github_url(remote_item)
            break

    if not base_url:
        raise RuntimeError('Not remote found for {}'.format(remote))

    if not branch:
        branch = get_current_branch()

    url = base_url + '/blame/{branch}/{path}#L{line}'.format(
        branch=branch, path=relative_path, line=line)
    return url


def open_url(url):
    run_cmd(['xdg-open', url])


def main():
    argc = len(argv)
    if argc < 3:
        print('Usage: %s RELATIVE_FILE LINE_NUMBER [REMOTE=origin] [BRANCH]' % argv[0], file=stderr)
        exit(1)
    open_url(blame(*argv[1:]))


if __name__ == '__main__':
    main()
