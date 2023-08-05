from cmdi import CmdResult, command
from buildlib import yaml
from buildlib.semver import prompt as semver_prompt


@command
def bump_version(
    semver_num: str = None,
    config_file: str = 'Project',
    **cmdargs,
) -> CmdResult:

    cfg: dict = yaml.loadfile(
        config_file,
        keep_order=True
    )

    if not semver_num:
        semver_num = semver_prompt.semver_num_by_choice(cfg['version'])

    cfg.update({'version': semver_num})

    yaml.savefile(cfg, config_file)

    return semver_num

