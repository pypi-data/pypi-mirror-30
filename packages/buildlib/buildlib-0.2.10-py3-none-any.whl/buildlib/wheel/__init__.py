from typing import Optional
import shutil
import os
import glob
from cmdi import CmdResult, command, set_result, strip_args
import subprocess as sp
from buildlib import semver
from buildlib.wheel import prompt


def extract_version_from_wheel_name(name: str) -> str:
    """
    Get the version part out of the wheel file name.
    """
    parted: list = name.split('-')
    return '' if len(parted) < 2 else parted[1]


def find_wheel(
    wheel_dir: str,
    semver_num: Optional[str] = None,
    wheelver_num: Optional[str] = None,
    raise_not_found: Optional[bool] = False,
) -> Optional[str]:
    """
    Search dir for a wheel-file which contains a specific version number in its
    name. Return found wheel name or False.
    """

    if wheelver_num:
        requested_version: str = wheelver_num

    elif semver_num:
        requested_version: str = semver.convert_semver_to_wheelver(semver_num)

    else:
        raise ValueError(
            'No version provided. Please provide either semver_num or '
            'wheelver_num.'
        )

    files: list = [file for file in os.listdir(wheel_dir)]

    matches: list = [
        file for file in files
        if extract_version_from_wheel_name(file) == requested_version
    ]

    if matches:
        return wheel_dir + '/' + matches[0]

    elif not matches and raise_not_found:
        raise FileNotFoundError('Could not find wheel file.')

    else:
        return None


class cmd:

    @staticmethod
    @command
    def push_to_gemfury(wheel_file: str, **cmdargs) -> CmdResult:
        return set_result(push_to_gemfury(**strip_args(locals())))

    @staticmethod
    @command
    def push(
        repository='pypi', clean_dir: bool = False, **cmdargs
    ) -> CmdResult:
        return set_result(push(**strip_args(locals())))

    @staticmethod
    @command
    def build(clean_dir: bool = False, **cmdargs) -> CmdResult:
        return set_result(build(**strip_args(locals())))


def push_to_gemfury(wheel_file: str, ) -> None:
    """"""
    sp.run(
        ['fury', 'push', wheel_file],
        check=True,
    )


def _clean_bdist_tmp_files() -> None:
    """"""
    build_dir: str = f'{os.getcwd()}/build'
    egg_file: list = glob.glob('**.egg-info')
    egg_file: str = egg_file and egg_file[0] or ''

    os.path.isdir(build_dir) and shutil.rmtree(build_dir)
    os.path.isdir(egg_file) and shutil.rmtree(egg_file)


def push(
    repository='pypi',
    clean_dir: bool = False,
) -> None:
    """"""
    sp.run(
        ['python', 'setup.py', 'bdist_wheel', 'upload', '-r', repository],
        check=True,
    )

    if clean_dir:
        _clean_bdist_tmp_files()


def build(clean_dir: bool = False, ) -> None:
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
