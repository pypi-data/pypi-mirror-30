from base64 import b64encode
import string
import random
import json
import re
import subprocess as sp
from typing import Optional, List, Pattern
from buildlib.kubernetes import cmd


def generate_password(length: int = 32):
    """
    Generate a base64 encoded string consisting of numbers and upper/lower case
    ascii letters.
    Kubernetes requires base64 encoding.
    """
    rand_items = (
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _
        in range(length)
    )
    s = ''.join(rand_items)
    s = b64encode(s.encode()).decode('utf8')

    return s


def get_pod_name(
    label: str,
    namespace: str,
    namefilter: Optional[Pattern] = None,
    statusfilter: Optional[Pattern]=None,
    **cmdargs,
) -> Optional[List[str]]:

    result = sp.run(
        ['kubectl', 'get', 'po', '-n', namespace, '-l', label, '-o', 'json'],
        check=True,
        stdout=sp.PIPE,
    )

    output = result.stdout.decode()
    data = json.loads(output)
    pods = data.get('items')
    pod_names = []

    for pod in pods:
        name = pod.get('metadata', {}).get('name')


        try:
            state = pod.get('status', {}).get('containerStatuses', [])[0].get('state')
        except KeyError:
            state = {}

        if namefilter and not re.search(namefilter, name):
            continue

        if statusfilter:
            if not any([re.search(statusfilter, k) for k in state.keys()]):
                continue

        pod_names.append(name)

    return pod_names

