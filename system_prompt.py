import config as cfg
from training import load_examples

# Mutable reference held at module level so routes can read and update it.
_prompt: list[str] = [cfg.SYSTEM_PROMPT + load_examples()]


def get() -> str:
    return _prompt[0]


def set(value: str) -> None:
    _prompt[0] = value
