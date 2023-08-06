import string
import random
from datetime import datetime, timezone
import json
import time
import sys
import re
from base64 import b64encode
import subprocess as sp
from typing import Optional, List, Pattern, Union
from cmdi import command, CmdResult, set_result, strip_args
from buildlib.kubernetes import helm


def parse_option(
    flag: str,
    val: Union[List[str], bool],
    sep: 'str' = '',
) -> list:
    """"""
    if flag in ['', None]:
        flag = []
    else:
        flag = [flag]

    if type(val) == str:
        return flag + [val]
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
        statusfilter: Optional[List[str]] = None,
        minage: int = None,
        maxage: int = None,
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

    @staticmethod
    @command
    def logs(
        namespace: List[str],
        name: Optional[List[str]] = None,
        follow: bool = False,
        **cmdargs
    ) -> None:
        return logs(**strip_args(locals()))


def get_item_names(
    namespace: List[str],
    kind: List[str],
    label: Optional[List[str]] = None,
    namefilter: Optional[Pattern] = None,
    statusfilter: Optional[List[str]] = None,
    minage: int = None,
    maxage: int = None,
) -> Optional[List[str]]:
    """
    @statusfilter: can be:
      Running, Terminating, Error, CrashLoopBackOff, ContainerCreating.
    """

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

            state = item\
            .get('status', {})\
            .get('containerStatuses',[])[0]\
            .get('state', {})

            if state.get('waiting', {}).get('reason') == "ContainerCreating":
                status = 'ContainerCreating'

            elif state.get('running', None):
                status = 'Running'

            elif state.get('waiting', {}).get('reason') == "CrashLoopBackOff":
                status = 'CrashLoopBackOff'

            elif state.get('terminated', {}).get('reason') == "Error":
                status = 'Error'

            elif state.get('terminated', {}).get('exitCode') in ['0', 0]:
                status = 'Terminating'

            else:
                status = None

        except IndexError:
            state = {}
            status = ''

        try:
            key = list(state.keys())[0]
            started_date = item\
            .get('status', {})\
            .get('containerStatuses', [])[0]\
            .get('state', {}).get(key, {}).get('startedAt')

        except IndexError:
            started_date = None

        if started_date:
            started_tuple = time.strptime(started_date, "%Y-%m-%dT%H:%M:%SZ")
            started_ts = time.mktime(started_tuple)
            now_ts = time.mktime(datetime.now(timezone.utc).timetuple())
            age = now_ts - started_ts
        else:
            age = None

        if namefilter and not re.search(namefilter, name):
            continue

        if statusfilter and not status in statusfilter:
            continue

        if minage and age:
            if age <= minage:
                continue

        if maxage and age:
            if age >= maxage:
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


def logs(
    namespace: List[str],
    name: Optional[List[str]] = None,
    follow: bool = False,
) -> None:
    """
    @name: podname
    kubectl logs -n mw-prod logcenter-api-5ddd8ff4bc-q5ccs
    """
    options = [
        *parse_option('', name, sep=' '),
        *parse_option('-n', namespace, sep=','),
        *parse_option('--follow', follow, sep=''),
    ]

    sp.run(
        ['kubectl', 'logs'] + options,
        check=True,
    )
