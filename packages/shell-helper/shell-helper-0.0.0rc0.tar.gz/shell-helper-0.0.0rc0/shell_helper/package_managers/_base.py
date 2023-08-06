from shell_helper.bases import which, run_cmd


class PackageManagerException(BaseException):
    pass


class InstallationFailed(PackageManagerException):
    pass


class RemovalFailed(PackageManagerException):
    pass


class SyncFailed(PackageManagerException):
    pass


def requires_success_or(exc=PackageManagerException):
    def _dec(fn):
        def _callback(*args, **kwargs):
            ret = fn(*args, **kwargs)

            if ret.returncode != 0:
                raise exc(repr((args, kwargs)))

            return ret
        return _callback
    return _dec


class BasePackageManager:
    IS_UP_TO_DATE = False

    @classmethod
    def is_package_manager_available(cls):
        return which(cls.CMD) is not None

    @classmethod
    def is_installed(cls, package_name) -> bool:
        pass

    @classmethod
    def sync(cls):
        pass

    @classmethod
    def install(cls, *package_name):
        if not cls.IS_UP_TO_DATE:
            cls.sync()
            cls.IS_UP_TO_DATE = True

    @classmethod
    def remove(cls, *package_name):
        pass


__all__ = [
    'BasePackageManager', 'PackageManagerException', 'InstallationFailed', 'RemovalFailed', 'SyncFailed',
    'requires_success_or', 'run_cmd'
]
