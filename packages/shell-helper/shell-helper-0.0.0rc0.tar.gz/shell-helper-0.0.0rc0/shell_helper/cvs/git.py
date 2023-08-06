from shell_helper.base_command import ShellCommand
from shell_helper.bases import split_line

git = ShellCommand("git")

init = git.register_simple('init')

remote = git.register_simple('remote')
remote_add = remote.register_simple('add')
remote_remove = remote.register_simple('remove')
remote_get_url = remote.register_simple('get-url')


class GitRemoteEntry(object):
    __slots__ = ('remote', 'url', 'type')

    def __init__(self, remote_name, url, type_):
        self.remote = remote_name
        self.url = url
        self.type = type_

    def __repr__(self):
        return '<{0.__class__.__name__} {0}>'.format(self)

    def __str__(self):
        return '{0.remote} {0.url} ({0.type})'.format(self)


def _parse_remote(line: str):
    args = split_line(line)
    args[-1] = args[-1].strip('()')
    return GitRemoteEntry(*args)


def get_remote_list():
    response = remote.run('--verbose', strict=True)
    result = []
    for line in response.stdout.decode('utf-8').split('\n'):
        if line:
            result.append(_parse_remote(line))
    return result
