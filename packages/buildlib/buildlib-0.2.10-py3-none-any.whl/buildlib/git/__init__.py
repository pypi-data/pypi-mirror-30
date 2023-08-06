import subprocess as sp
from typing import Optional
from cmdi import command, CmdResult, set_result, strip_args
from buildlib.git import prompt, seq


class cmd:

    @staticmethod
    @command
    def add_all() -> CmdResult:
        return set_result(add_all(**strip_args(locals())))

    @staticmethod
    @command
    def commit(msg: str) -> CmdResult:
        return set_result(commit(**strip_args(locals())))

    @staticmethod
    @command
    def tag(
        version: str,
        branch: str,
    ) -> CmdResult:
        return set_result(tag(**strip_args(locals())))

    @staticmethod
    @command
    def push(branch: str) -> CmdResult:
        return set_result(push(**strip_args(locals())))

    @staticmethod
    @command
    def get_default_branch() -> CmdResult:
        return set_result(get_default_branch(**strip_args(locals())))

    @staticmethod
    @command
    def status() -> CmdResult:
        return set_result(status(**strip_args(locals())))

    @staticmethod
    @command
    def diff() -> CmdResult:
        return set_result(diff(**strip_args(locals())))


def add_all() -> None:
    """"""
    sp.run(
        ['git', 'add', '--all'],
        check=True,
    )


def commit(msg: str) -> None:
    """"""
    sp.run(
        ['git', 'commit', '-m', msg],
        check=True,
    )


def tag(
    version: str,
    branch: str,
) -> None:
    """"""
    sp.run(
        ['git', 'tag', version, branch],
        check=True,
    )


def push(branch: str) -> None:
    """"""
    sp.run(
        ['git', 'push', 'origin', branch, '--tags'],
        check=True,
    )


def get_default_branch() -> str:
    """"""
    branch: Optional[str] = None

    p1 = sp.run(
        ['git', 'show-branch', '--list'],
        stdout=sp.PIPE,
        check=True,
    )

    if p1.stdout.decode().find('No revs') == -1 and p1.returncode == 0:
        p2 = sp.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=sp.PIPE,
            check=True,
        )

        branch: str = p2.stdout.decode().replace('\n', '')

    return branch


def status() -> None:
    """"""
    sp.run(
        ['git', 'status'],
        check=True,
    )


def diff() -> None:
    """"""
    sp.run(
        ['git', 'diff'],
        check=True,
    )
