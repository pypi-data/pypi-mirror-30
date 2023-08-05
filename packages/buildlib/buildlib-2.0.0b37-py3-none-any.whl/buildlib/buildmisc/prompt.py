import prmt


def should_run_any(
        name: str,
        default: str = '',
        margin: tuple = (1, 1),
) -> bool:

    return prmt.confirm(
        question=f'Run ANY {name}?\n',
        default=default,
        margin=margin,
    )


def should_run_file(
        name: str,
        default: str = '',
        margin: tuple = (1, 1),
) -> bool:

    return prmt.confirm(
        question=f'Do you want to RUN {name}?\n',
        default=default,
        margin=margin)


def should_build(
        item: str,
        default: str = '',
        margin: tuple = (1, 1),
) -> bool:

    return prmt.confirm(
        question=f'Do you want to BUILD {item}?\n',
        default=default,
        margin=margin)


def should_push(
        item: str,
        dst: str,
        default: str = '',
        margin: tuple = (1, 1),
) -> bool:

    return prmt.confirm(
        question=f'Do you want to PUSH {item} to {dst}?\n',
        default=default,
        margin=margin)
