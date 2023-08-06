from typing import Optional, List, Pattern, Union
from cmdi import command, CmdResult, strip_args
import subprocess as sp
from buildlib.kubernetes import parse_option


class cmd:

    @staticmethod
    @command
    def update(
        name: str,
        namespace: List[str],
        force: bool = False,
        recreate_pods: bool = False,
        **cmdargs
    ) -> CmdResult:
        return update(**strip_args(locals()))


def update(
    name: str,
    namespace: List[str],
    force: bool = False,
    recreate_pods: bool = False,
) -> None:
    """
    helm upgrade logcenter --force --recreate-pods --namespace mw-prod chart
    """

    options = [
        *parse_option(flag='', val=name, sep=''),
        *parse_option(flag='-n', val=namespace, sep=','),
        *parse_option(flag='--force', val=force, sep=''),
    ]

    sp.run(
        ['helm', 'update'] + options,
        check=True,
    )
