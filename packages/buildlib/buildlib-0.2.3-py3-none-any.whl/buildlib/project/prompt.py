import prmt


def should_bump_version(
        default: str = 'y',
        margin: tuple = (1, 1),
) -> bool:

    return prmt.confirm(
        question='BUMP VERSION number?\n',
        default=default,
        margin=margin,
    )
