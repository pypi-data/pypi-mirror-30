from typing import Optional, List
from buildlib import git
from cmdi import CmdResult


class GitSeqSettings:
    version: str = None
    new_release: bool = True
    should_run_any: bool = True
    should_add_all: bool = True
    should_commit: bool = True
    commit_msg: str = 'No comment message.'
    should_tag: bool = True
    should_push: bool = True
    branch: str = 'master'


def get_settings_from_user(
    version: str,
    new_release: bool,
) -> GitSeqSettings:

    s = GitSeqSettings()

    s.version = version
    s.new_release = new_release

    # Ask user to check status.
    if not git.prompt.confirm_status('y'):
        s.should_run_any = False
        return s

    # Ask user to check diff.
    if not git.prompt.confirm_diff('y'):
        s.should_run_any = False
        return s

    # Ask user to run 'git add -A.
    s.should_add_all: bool = git.prompt.should_add_all(default='y')

    # Ask user to run commit.
    s.should_commit: bool = git.prompt.should_commit(default='y')

    # Get commit msg from user.
    if s.should_commit:
        s.commit_msg: str = git.prompt.commit_msg()

    # Ask user to run 'tag'.
    s.should_tag: bool = git.prompt.should_tag(
        default='y' if s.new_release is True else 'n'
    )

    # Ask user to push.
    s.should_push_git: bool = git.prompt.should_push(default='y')

    # Ask user for branch.
    if any([s.should_tag, s.should_push_git]):
        s.branch: str = git.prompt.branch()

    return s


def bump_sequence(s: GitSeqSettings) -> List[CmdResult]:
    """"""
    results = []

    # If any git commands should be run.
    if not s.should_run_any:
        return results

    # Run 'add -A'
    if s.should_add_all:
        results.append(git.cmd.add_all())

    # Run 'commit -m'
    if s.should_commit:
        results.append(git.cmd.commit(s.commit_msg))

    # Run 'tag'
    if s.should_tag:
        results.append(git.cmd.tag(s.version, s.branch))

    # Run 'push'
    if s.should_push:
        results.append(git.cmd.push(s.branch))

    return results


def bump_git(
    version: str,
    new_release: bool = True,
):
    s = get_settings_from_user(version, new_release)
    return bump_sequence(s)
