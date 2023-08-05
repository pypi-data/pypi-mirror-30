import string
import random
import json
import sys
import re
from base64 import b64encode
import subprocess as sp
from typing import Optional, List, Pattern, Union
from cmdi import command, CmdResult, set_result, strip_args


def parse_kubectl_option(
    flag: str,
    args: List[str],
    sep: 'str',
) -> list:
    """"""
    if flag in ['', None]:
        flag = []
    else:
        flag = [flag]

    if type(args) == list:
        return flag + [sep.join(args)]
    else:
        return []


def generate_password(length: int = 32):
    """
    Generate a base64 encoded string consisting of numbers and upper/lower case
    ascii letters.
    Kubernetes requires base64 encoding.
    """
    rand_items = (
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )
    s = ''.join(rand_items)
    s = b64encode(s.encode()).decode('utf8')

    return s


class cmd:

    @staticmethod
    @command
    def get_item_names(
        namespace: List[str],
        kind: List[str],
        label: Optional[List[str]] = None,
        namefilter: Optional[Pattern] = None,
        statusfilter: Optional[Pattern] = None,
        **cmdargs
    ) -> CmdResult:
        return set_result(get_item_names(**strip_args(locals())))

    @staticmethod
    @command
    def apply(
        stdin: str = None,
        files: List[str] = None,
        namespace: List[str] = None,
        **cmdargs
    ) -> CmdResult:
        return apply(**locals())

    @staticmethod
    @command
    def delete(
        namespace: List[str],
        kind: Optional[List[str]] = None,
        name: Optional[List[str]] = None,
        label: Optional[List[str]] = None,
        **cmdargs
    ) -> CmdResult:
        return delete(**locals())


def get_item_names(
    namespace: List[str],
    kind: List[str],
    label: Optional[List[str]] = None,
    namefilter: Optional[Pattern] = None,
    statusfilter: Optional[Pattern] = None,
) -> Optional[List[str]]:

    kind = parse_kubectl_option('', kind, sep=',')

    options = [
        *parse_kubectl_option('-n', namespace, sep=','),
        *parse_kubectl_option('-l', label, sep=','),
    ]

    result = sp.run(
        ['kubectl', 'get'] + kind + options + ['-o', 'json'],
        check=True,
        stdout=sp.PIPE,
    )

    output = result.stdout.decode()
    data = json.loads(output)
    items = data.get('items')
    item_names = []

    for item in items:
        name = item.get('metadata', {}).get('name')

        try:
            state = item.get('status', {}).get('containerStatuses',
                                               [])[0].get('state')
        except IndexError:
            state = {}

        if namefilter and not re.search(namefilter, name):
            continue

        if statusfilter:
            if not any([re.search(statusfilter, k) for k in state.keys()]):
                continue

        item_names.append(name)

    return item_names


def apply(
    stdin: str = None,
    files: List[str] = None,
    namespace: List[str] = None,
) -> None:
    """
    @std: Use this to pass a config string via stdin.
    """
    if stdin and files:
        raise ValueError(
            'Cannot use parameter "stdin" and "files" at the same time'
        )

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


def delete(
    namespace: List[str],
    kind: Optional[List[str]] = None,
    name: Optional[List[str]] = None,
    label: Optional[List[str]] = None,
) -> None:
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
