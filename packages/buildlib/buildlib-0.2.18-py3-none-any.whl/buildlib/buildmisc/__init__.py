"""
Misc build commands.
Everything that does not deserve it's own package goes here.
"""

import os
import shutil
import glob
import subprocess as sp
from typing import Optional, List, Pattern, Union
from cmdi import command, CmdResult, set_result, strip_args
from buildlib.buildmisc import prompt
from buildlib import yaml, module
from buildlib.semver import prompt as semver_prompt


class cmd:

    @staticmethod
    @command
    def inject_interface_into_readme(
        interface_file: str, readme_file: str = 'README.md', **cmdargs
    ) -> CmdResult:
        return set_result(inject_interface_into_readme(**strip_args(locals())))

    @staticmethod
    @command
    def build_read_the_docs(clean_dir: bool = False, **cmdargs) -> CmdResult:
        return set_result(build_read_the_docs(**strip_args(locals())))

    @staticmethod
    @command
    def create_py_venv(py_bin: str, venv_dir: str, **cmdargs) -> CmdResult:
        return set_result(create_py_venv(**strip_args(locals())))


def inject_interface_into_readme(
    interface_file: str,
    readme_file: str = 'README.md',
) -> None:
    """
    Add content of help.txt into README.md
    Content of help.txt will be placed into the first code block (```) of README.md.
    If no code block is found, a new one will be added to the beginning of README.md.
    """
    readme_str: str = open(readme_file, 'r').read()
    interface_str = open(interface_file, 'r').read()

    help_str: str = f'```\n{interface_str}\n```'

    start: int = readme_str.find('```') + 3
    end: int = readme_str.find('```', start)

    if '```' in readme_str:
        mod_str: str = readme_str[0:start - 3] + help_str + readme_str[end + 3:]
    else:
        mod_str: str = help_str + readme_str

    with open('README.md', 'w') as modified_readme:
        modified_readme.write(mod_str)


def build_read_the_docs(clean_dir: bool = False) -> None:
    """"""

    build_dir = f'{os.getcwd()}/docs/build'

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    sp.run(
        ['make', 'html'],
        cwd='{}/docs'.format(os.getcwd()),
        check=True,
    )


def create_py_venv(
    py_bin: str,
    venv_dir: str,
) -> None:
    """
    NOTE: Consider useing pipenv.

    @interpreter: must be the exact interpreter name. E.g. 'python3.5'
    """
    sp.run(
        [py_bin, '-m', 'venv', venv_dir],
        check=True,
    )
