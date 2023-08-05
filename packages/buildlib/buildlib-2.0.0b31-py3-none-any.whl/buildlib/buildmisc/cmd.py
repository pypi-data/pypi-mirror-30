"""
Misc build commands.
Everything that does not deserve it's own package goes here.
"""

import os
import shutil
import glob
import subprocess as sp
from cmdi import command, CmdResult, CustomCmdResult
from buildlib import yaml, module
from buildlib.semver import prompt as semver_prompt


@command
def inject_interface_txt_into_readme_md(
    interface_file: str,
    readme_file: str = 'README.md',
    **cmdargs,
) -> CmdResult:
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


@command
def build_read_the_docs(
    clean_dir: bool = False,
    **cmdargs,
) -> CmdResult:
    """"""
    build_dir = f'{os.getcwd()}/docs/build'

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    sp.run(
        ['make', 'html'],
        cwd='{}/docs'.format(os.getcwd()),
        check=True,
    )


@command
def create_py_venv(
    py_bin: str,
    venv_dir: str,
    **cmdargs,
) -> CmdResult:
    """
    NOTE: Consider useing pipenv.

    @interpreter: must be the exact interpreter name. E.g. 'python3.5'
    """
    sp.run(
        [py_bin, '-m', 'venv', venv_dir],
        check=True,
    )

