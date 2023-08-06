from typing import Optional, List, Pattern, Union
from cmdi import command, CmdResult, strip_args
import subprocess as sp
from buildlib import kubernetes as kube


class cmd:

    @staticmethod
    @command
    def update(
        release: str,
        chart: str,
        namespace: List[str],
        force: bool = False,
        recreate_pods: bool = False,
        **cmdargs
    ) -> CmdResult:
        return update(**strip_args(locals()))


def update(
    release: str,
    chart: str,
    namespace: List[str],
    force: bool = False,
    recreate_pods: bool = False,
) -> None:
    """
    helm upgrade logcenter chart --force --recreate-pods --namespace mw-prod
    """
    options = [
        *kube.parse_option(flag='', val=release, sep=''),
        *kube.parse_option(flag='', val=chart, sep=''),
        *kube.parse_option(flag='--namespace', val=namespace, sep=','),
        *kube.parse_option(flag='--force', val=force, sep=''),
        *kube.parse_option(flag='--recreate-pods', val=recreate_pods, sep=''),
    ]

    sp.run(
        ['helm', 'upgrade'] + options,
        check=True,
    )
