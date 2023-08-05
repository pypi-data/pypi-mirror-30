import prmt


def should_build(
        default: str = 'y',
        margin: tuple = (1, 1),
) -> bool:

    return prmt.confirm(
        question=f'Do you want to BUILD WHEEL?\n',
        default=default,
        margin=margin)


def should_push(
        dst: str,
        default: str = 'y',
        margin: tuple = (1, 1),
) -> bool:

    return prmt.confirm(
        question=f'Do you want to PUSH WHEEL to {dst}?\n',
        default=default,
        margin=margin)
