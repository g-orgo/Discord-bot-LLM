import config as cfg

# Mutable reference held at module level so routes can read and update it.
_prompt: list[str] = [cfg.SYSTEM_PROMPT]


def get() -> str:
    return _prompt[0]


def set(value: str) -> None:
    _prompt[0] = value
