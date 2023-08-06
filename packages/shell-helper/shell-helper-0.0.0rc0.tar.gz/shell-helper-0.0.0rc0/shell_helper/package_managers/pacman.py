from ._base import *


class Pacman(BasePackageManager):
    CMD = '/usr/bin/pacman'

    @classmethod
    def is_package_manager_available(cls):
        return super(Pacman, cls).is_package_manager_available()

    @classmethod
    def is_installed(cls, package_name) -> bool:
        raise NotImplementedError

    @classmethod
    @requires_success_or(SyncFailed)
    def sync(cls):
        super(Pacman, cls).sync()
        return run_cmd([cls.CMD, '-Sy', '--noconfirm'], timeout=60)

    @classmethod
    @requires_success_or(InstallationFailed)
    def install(cls, *package_name):
        super(Pacman, cls).install()
        return run_cmd([cls.CMD, '-S', '--noconfirm'] + list(package_name), timeout=60)

    @classmethod
    @requires_success_or(RemovalFailed)
    def remove(cls, *package_name):
        super(Pacman, cls).remove()
        return run_cmd([cls.CMD, '-Rnds', '--noconfirm'] + list(package_name), timeout=60)


__all__ = ['Pacman']
