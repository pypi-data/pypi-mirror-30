from .aptitude import *
from .pacman import *


def get_package_manager():
    for cls in (Aptitude, Pacman):
        if cls.is_package_manager_available():
            return cls
