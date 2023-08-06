import shutil
import logging
import subprocess


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


WHITE_SPACES = ' \n\t'


def which(arg):
    return shutil.which(arg)


def run_cmd(args, **kwargs):
    kwargs.setdefault('timeout', 5)
    kwargs.setdefault('stdout', subprocess.PIPE)
    logger.info('Running: %r', args)
    return subprocess.run(args, **kwargs)


def is_success(r: subprocess.CompletedProcess):
    return r.returncode == 0


def split_line(line: str):
    args = []
    arg = ''

    def _append(_argument):
        if _argument:
            args.append(_argument)
            return ''
        return _argument

    for c in line:
        if c in WHITE_SPACES:
            arg = _append(arg)
        else:
            arg += c

    _append(arg)
    return args
