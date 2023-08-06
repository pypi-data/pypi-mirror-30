from ._base import *


class Aptitude(BasePackageManager):
    CMD = '/usr/bin/apt-get'

    @classmethod
    def is_package_manager_available(cls):
        return super(Aptitude, cls).is_package_manager_available()

    @classmethod
    def is_installed(cls, package_name) -> bool:
        raise NotImplementedError

    @classmethod
    @requires_success_or(SyncFailed)
    def sync(cls):
        super(Aptitude, cls).sync()
        return run_cmd([cls.CMD, 'update', '-y'], timeout=60)

    @classmethod
    @requires_success_or(InstallationFailed)
    def install(cls, *package_name):
        super(Aptitude, cls).install()
        return run_cmd([cls.CMD, 'install', '-y'] + list(package_name), timeout=60)

    @classmethod
    @requires_success_or(RemovalFailed)
    def remove(cls, *package_name):
        super(Aptitude, cls).remove()
        return run_cmd([cls.CMD, 'autoremove', '-y'] + list(package_name), timeout=60)


__all__ = ['Aptitude']
