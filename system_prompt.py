import config as cfg
from training import load_examples, load_few_shot_messages

# Separate mutable base from immutable examples so PUT /system-prompt never
# strips the few-shot training block.
_base: list[str] = [cfg.SYSTEM_PROMPT]
_examples: str = load_examples()
_few_shot_messages: list[dict] = load_few_shot_messages()


def get_base() -> str:
    return _base[0]


def get() -> str:
    return get_base() + _examples


def get_few_shot() -> list[dict]:
    """Return few-shot user/assistant message pairs for small-model guidance."""
    return _few_shot_messages


def set(value: str) -> None:
    """Replace only the base instruction block; training examples are preserved."""
    _base[0] = value
