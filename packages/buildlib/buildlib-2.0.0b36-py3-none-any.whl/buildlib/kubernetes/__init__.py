from base64 import b64encode
import string
import random
import json
import re
import subprocess as sp
from typing import Optional, List, Pattern


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
        for _
        in range(length)
    )
    s = ''.join(rand_items)
    s = b64encode(s.encode()).decode('utf8')

    return s


def get_item_names(
    namespace: List[str],
    kind: List[str],
    label: Optional[List[str]] = None,
    namefilter: Optional[Pattern] = None,
    statusfilter: Optional[Pattern]=None,
    **cmdargs,
) -> Optional[List[str]]:


    kind = parse_kubectl_option('', kind, sep=',')

    options = [
        *parse_kubectl_option('-n', namespace, sep=','),
        *parse_kubectl_option('-l', label, sep=','),
    ]

    result = sp.run(
        ['kubectl', 'get' ] + kind + options + ['-o', 'json'],
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
            state = item.get('status', {}).get('containerStatuses', [])[0].get('state')
        except IndexError:
            state = {}

        if namefilter and not re.search(namefilter, name):
            continue

        if statusfilter:
            if not any([re.search(statusfilter, k) for k in state.keys()]):
                continue

        item_names.append(name)

    return item_names
