import subprocess

from shell_helper.package_managers import get_package_manager
from shell_helper.bases import run_cmd, which, is_success


class MissingCommand(BaseException):
    pass


class CommandFailed(BaseException):
    def __init__(self, command, process: subprocess.CompletedProcess):
        self.process = process
        self.code = process.returncode
        self.command = command
        super(CommandFailed, self).__init__('{0.command} returned {0.code}'.format(self))


class ShellCommand:
    __slots__ = ('name', 'from_package', 'default_args')

    PACKAGE_MANAGER = get_package_manager()

    def __init__(self, name: str, from_package: str=None, *default_args):
        self.name = name

        # if from package is not set, and the command is not absolute
        if from_package is None and not name.startswith('/'):
            from_package = name
        self.from_package = from_package
        self.default_args = default_args

    def __repr__(self):
        return '<{} {} @ {}>'.format(
            self.__class__.__name__,
            ' '.join([
                '%s=%s' % (k, getattr(self, k)) for k in self.__slots__
            ]),
            id(self))

    def __str__(self):
        return ' '.join((self.name, ) + self.default_args)

    @property
    def installed(self):
        return which(self.name) is not None

    def install(self):
        if not self.from_package:
            raise MissingCommand(
                'Could not install \'{}\' through the package manager (missing package)'.format(self.name))

        ShellCommand.PACKAGE_MANAGER.install(self.from_package)
        assert self.installed is True

    def run(self, *args, **kwargs):
        strict = kwargs.get('strict', False)
        args = (self.name, ) + self.default_args + args
        r = run_cmd(args)
        if strict and not is_success(r):
            raise CommandFailed(' '.join(args), r)
        return r

    def copy(self, *args):
        instance = ShellCommand(self.name, self.from_package, *self.default_args, *args)
        return instance

    def register_simple(self, *args):
        instance = self.copy(*args)
        return instance
