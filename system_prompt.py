import config as cfg
from training import load_examples

# Separate mutable base from immutable examples so PUT /system-prompt never
# strips the few-shot training block.
_base: list[str] = [cfg.SYSTEM_PROMPT]
_examples: str = load_examples()


def get() -> str:
    return _base[0] + _examples


def set(value: str) -> None:
    """Replace only the base instruction block; training examples are preserved."""
    _base[0] = value
