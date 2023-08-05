import re
import subprocess as sp
from typing import Optional, Pattern, NamedTuple, Union, List
from buildlib.util import eprint
from functools import reduce
from cmdi import command, CmdResult, set_result, strip_args


class cmd:
    @staticmethod
    @command
    def get_images(
        interface_file: str, readme_file: str = 'README.md', **cmdargs
    ) -> CmdResult:
        return set_result(get_images(**strip_args(locals())))

    @staticmethod
    @command
    def run_container(
        image: str,
        add_host: Optional[List[str]] = None,
        env: Optional[List[str]] = None,
        network: Optional[str] = None,
        publish: Optional[List[str]] = None,
        volume: Optional[List[str]] = None,
        **cmdargs
    ) -> CmdResult:
        return set_result(run_container(**strip_args(locals())))

    @staticmethod
    @command
    def stop_container(by_port: Union[int, str], **cmdargs) -> CmdResult:
        return set_result(stop_container(**strip_args(locals())))

    @staticmethod
    @command
    def kill_container(by_port: Union[int, str], **cmdargs) -> CmdResult:
        return set_result(kill_container(**strip_args(locals())))

    @staticmethod
    @command
    def remove_image(image: str, force: bool = True, **cmdargs) -> CmdResult:
        return set_result(remove_image(**strip_args(locals())))

    @staticmethod
    @command
    def rm_dangling_images(force: bool = True, **cmdargs) -> CmdResult:
        return set_result(rm_dangling_images(**strip_args(locals())))

    @staticmethod
    @command
    def tag_image(
        src_image: str,
        registry: Optional[str] = None,
        namespace: Optional[str] = None,
        dst_image: Optional[str] = None,
        tag_latest: Optional[bool] = False,
        **cmdargs
    ) -> CmdResult:
        return set_result(tag_image(**strip_args(locals())))

    @staticmethod
    @command
    def push_image(
        image: str,
        registry: Optional[str] = None,
        namespace: Optional[str] = None,
        **cmdargs
    ) -> CmdResult:
        return set_result(push_image(**strip_args(locals())))

    @staticmethod
    @command
    def build_image(
        tag: List[str],
        build_arg: List[str] = None,
        dockerfile: str = 'Dockerfile',
        **cmdargs
    ) -> CmdResult:
        return set_result(build_image(**strip_args(locals())))


def _parse_option(
    args: Union[bool, list, str],
    flag: str,
) -> list:
    """"""
    if type(args) == list:
        nested = [[flag, f] for f in args]
        return reduce(lambda x, y: x + y, nested)
    elif type(args) == str:
        return [flag, args]
    elif type(args) == bool:
        return [flag] if args is True else []
    else:
        return []


class Image(NamedTuple):
    num: int
    repository: str
    tag: str
    id: str
    created: str
    size: str


def get_images(
    repository: Optional[Union[bytes, str, Pattern]] = None,
    tag: Optional[Union[bytes, str, Pattern]] = None,
    id: Optional[Union[bytes, str, Pattern]] = None,
    created: Optional[Union[bytes, str, Pattern]] = None,
    size: Optional[Union[bytes, str, Pattern]] = None,
) -> Optional[List[Image]]:
    """"""
    kwargs = locals()
    result = sp.run(['docker', 'images'], stdout=sp.PIPE)

    output = result.stdout.decode()

    images = []
    new_images = []
    count = 0

    for raw_line in output.split('\n'):
        if raw_line:
            cols = re.split('[ \t]{3,}', raw_line)

        if cols[0] == 'REPOSITORY':
            continue

        if len(cols) == 5:
            images.append(
                Image(count, cols[0], cols[1], cols[2], cols[3], cols[4])
            )
            count += 1
        else:
            eprint('Error: cannot interpret line in output:\n' + raw_line)

    for image in images:
        for _, val in kwargs.items():
            if val:
                if re.search(val, image.repository):
                    new_images.append(image)
                    continue

    return new_images or None


def run_container(
    image: str,
    add_host: Optional[List[str]] = None,
    env: Optional[List[str]] = None,
    network: Optional[str] = None,
    publish: Optional[List[str]] = None,
    volume: Optional[List[str]] = None,
) -> None:
    """
    Run Docker container locally.
    """
    options = [
        *_parse_option(add_host, '--add-host'),
        *_parse_option(env, '-e'),
        *_parse_option(network, '--network'),
        *_parse_option(publish, '-p'),
        *_parse_option(volume, '-v'),
    ]

    sp.run(
        ['docker', 'run', '-d'] + options + [image],
        check=True,
    )


def stop_container(by_port: Union[int, str]) -> None:
    """"""
    cmd = [
        'docker', 'ps', '-q', '--filter', f'expose={by_port}',
        '--format="{{.ID}}"'
    ]

    result = sp.run(
        cmd,
        check=True,
        stdout=sp.PIPE,
    )

    ids = result.stdout.decode().split('\n')

    for id in ids:
        id and sp.run(['docker', 'stop', id.replace('"', '')], check=True)


def kill_container(by_port: Union[int, str]) -> None:
    """"""
    cmd = [
        'docker', 'ps', '-q', '--filter', f'expose={by_port}',
        '--format="{{.ID}}"'
    ]

    result = sp.run(
        cmd,
        check=True,
        stdout=sp.PIPE,
    )

    ids = result.stdout.decode().split('\n')

    for id in ids:
        id and sp.run(['docker', 'kill', id.replace('"', '')], check=True)


def _image_exists(image: str) -> bool:

    result = sp.run(
        ['docker', 'inspect', '--type=image', image],
        check=True,
        stdout=sp.PIPE,
    )

    stdout = result.stdout.decode()

    return 'Error: No such image' not in stdout


def remove_image(
    image: str,
    force: bool = True,
) -> None:

    if _image_exists(image):
        options = [
            *_parse_option(force, '--force'),
        ]

        sp.run(['docker', 'rmi', image] + options, check=True)


def rm_dangling_images(force: bool = True) -> None:

    result = sp.run(
        ['docker', 'images', '-f', 'dangling=true', '-q'],
        check=True,
        stdout=sp.PIPE,
    )

    ids = result.stdout.decode().split('\n')

    for id in ids:
        id and remove_image(id, force=force)


def tag_image(
    src_image: str,
    registry: Optional[str] = None,
    namespace: Optional[str] = None,
    dst_image: Optional[str] = None,
    tag_latest: Optional[bool] = False,
) -> None:

    registry = registry + '/' if registry else ''
    namespace = namespace + '/' if namespace else ''
    dst_image = dst_image or src_image

    cmds = [['docker', 'tag', src_image, f'{registry}{namespace}{dst_image}']]

    if tag_latest:
        base_name = re.search('.*[:]', dst_image) or dst_image
        latest = f'{base_name}:latest'

        tag_cmd = [
            'docker', 'tag', dst_image, f'{registry}{namespace}{latest}'
        ]

        cmds.insert(1, tag_cmd)

    for cmd in cmds:
        sp.run(cmd, check=True)


def push_image(
    image: str,
    registry: Optional[str] = None,
    namespace: Optional[str] = None,
) -> None:

    registry = registry + '/' if registry else ''
    namespace = namespace + '/' if namespace else ''

    sp.run(['docker', 'push', f'{registry}{namespace}{image}'], check=True)


def build_image(
    tag: List[str],
    build_arg: List[str] = None,
    dockerfile: str = 'Dockerfile',
) -> None:

    options = [
        *_parse_option(build_arg, '--build-arg'),
        *_parse_option(tag, '-t'),
    ]

    sp.run(
        ['docker', 'build', '.', '--pull', '-f', dockerfile] + options,
        check=True,
    )


if True: print('Hello')
