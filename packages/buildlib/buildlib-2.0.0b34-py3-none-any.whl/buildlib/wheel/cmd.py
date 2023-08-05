import os
import shutil
import glob
from cmdi import CmdResult, command
import subprocess as sp


@command
def push_to_gemfury(
    wheel_file: str,
    **cmdargs,
) -> CmdResult:
    """"""
    sp.run(
        ['fury', 'push', wheel_file],
        check=True
    )


def _clean_bdist_tmp_files() -> None:
    """"""
    build_dir: str = f'{os.getcwd()}/build'
    egg_file: list = glob.glob('**.egg-info')
    egg_file: str = egg_file and egg_file[0] or ''

    os.path.isdir(build_dir) and shutil.rmtree(build_dir)
    os.path.isdir(egg_file) and shutil.rmtree(egg_file)


@command
def push(
    repository='pypi',
    clean_dir: bool = False,
    **cmdargs,
) -> CmdResult:
    """"""
    sp.run(
        ['python', 'setup.py', 'bdist_wheel', 'upload', '-r', repository],
        check=True,
    )

    if clean_dir:
        _clean_bdist_tmp_files()


@command
def build(
    clean_dir: bool = False,
    **cmdargs,
) -> CmdResult:
    """
    @clean_dir: Clean 'build' dir before running build command. This may be necessary because of
    this: https://bitbucket.org/pypa/wheel/issues/147/bdist_wheel-should-start-by-cleaning-up
    """
    sp.run(
        ['python', 'setup.py', 'bdist_wheel'],
        check=True,
    )

    if clean_dir:
        _clean_bdist_tmp_files()

