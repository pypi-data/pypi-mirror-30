from cmdi import CmdResult, command, set_result, strip_args
import subprocess as sp


class cmd:

    @staticmethod
    @command
    def install(dev: bool = False) -> CmdResult:
        return set_result(install(**strip_args(locals())))

    @staticmethod
    @command
    def create_env(version: str) -> CmdResult:
        return set_result(create_env(**strip_args(locals())))


def install(dev: bool = False) -> None:
    """
    Install packages from Pipfile.
    """
    dev_flag = ['--dev'] if dev else []
    sp.run(
        ['pipenv', 'install'] + dev_flag,
        check=True,
    )


def create_env(version: str) -> None:
    """
    Create a fresh python environment.
    @version: E.g.: '3.6'
    """
    sp.run(
        ['pipenv', f'--python {version}'],
        check=True,
    )
