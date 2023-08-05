from typing import List, Union, Optional
import sys
import subprocess as sp
from cmdi import command, CmdResult, CustomCmdResult
from buildlib.kubernetes import parse_kubectl_option


@command
def apply(
    stdin: str = None,
    files: List[str] = None,
    namespace: List[str] = None,
    **cmdargs,
) -> CmdResult:
    """
    @std: Use this to pass a config string via stdin.
    """
    if stdin and files:
        raise ValueError('Cannot use parameter "stdin" and "files" at the same time')

    options = [
        *parse_kubectl_option('-n', namespace, sep=','),
        *parse_kubectl_option('-f', files, sep=','),
    ]

    cmd = ['kubectl', 'apply'] + options

    if stdin:
        cmd += ['-f', '-']

    p = sp.Popen(cmd, stdin=sp.PIPE)

    if stdin:
        p.stdin.write(stdin.encode())

    p.communicate()

    if p.returncode != 0:
        raise sp.CalledProcessError(p.returncode, cmd)


@command
def delete(
    namespace: List[str],
    kind: Optional[List[str]]= None,
    name: Optional[List[str]] = None,
    label: Optional[List[str]] = None,
    **cmdargs,
) -> CmdResult:
    """
    @type_: pods, replicaSets, deployments, etc'
    @name: podname
    """
    if kind and name:
        raise ValueError('You cannot use "name" and "kind" at the same time.')

    kind = parse_kubectl_option('', kind, sep=',')
    name = parse_kubectl_option('', name, sep=' ')

    options = [
        *parse_kubectl_option('-l', label, sep=','),
        *parse_kubectl_option('-n', namespace, sep=','),
    ]

    sp.run(
        ['kubectl', 'delete'] + kind + name + options,
        check=True,
    )
