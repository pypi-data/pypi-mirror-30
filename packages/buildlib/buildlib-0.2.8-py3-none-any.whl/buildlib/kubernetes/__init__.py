import string
import random
import json
import sys
import re
from base64 import b64encode
import subprocess as sp
from typing import Optional, List, Pattern, Union
from cmdi import command, CmdResult, set_result, strip_args


def parse_option(flag: str, val: Union[List[str], bool],
                 sep: 'str' = '') -> list:
    """"""
    if flag in ['', None]:
        flag = []
    else:
        flag = [flag]

    if type(val) == list:
        return flag + [sep.join(val)]
    elif type(val) == bool and val is True:
        return flag
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
        return get_item_names(**strip_args(locals()))

    @staticmethod
    @command
    def apply(
        stdin: str = None,
        files: List[str] = None,
        namespace: List[str] = None,
        **cmdargs
    ) -> CmdResult:
        return apply(**strip_args(locals()))

    @staticmethod
    @command
    def delete(
        namespace: List[str],
        kind: Optional[List[str]] = None,
        name: Optional[List[str]] = None,
        label: Optional[List[str]] = None,
        **cmdargs
    ) -> CmdResult:
        return delete(**strip_args(locals()))


def get_item_names(
    namespace: List[str],
    kind: List[str],
    label: Optional[List[str]] = None,
    namefilter: Optional[Pattern] = None,
    statusfilter: Optional[Pattern] = None,
) -> Optional[List[str]]:

    options = [
        *parse_option('', kind, sep=','),
        *parse_option('-n', namespace, sep=','),
        *parse_option('-l', label, sep=','),
    ]

    result = sp.run(
        ['kubectl', 'get'] + options + ['-o', 'json'],
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
    @stdin: Use this to pass in a config string via stdin.
    """
    if stdin and files:
        raise ValueError(
            'Cannot use parameter "stdin" and "files" at the same time'
        )

    options = [
        *parse_option('-n', namespace, sep=','),
        *parse_option('-f', files, sep=','),
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
    options = [
        *parse_option('', kind, sep=','),
        *parse_option('', name, sep=' '),
        *parse_option('-l', label, sep=','),
        *parse_option('-n', namespace, sep=','),
    ]

    sp.run(
        ['kubectl', 'delete'] + options,
        check=True,
    )
