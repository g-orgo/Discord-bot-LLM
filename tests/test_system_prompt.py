"""Unit tests for the system_prompt module (pure get/set logic)."""
import pytest
import system_prompt
import config as cfg


@pytest.fixture(autouse=True)
def reset_prompt():
    """Reset prompt to default before each test and restore after."""
    system_prompt.set(cfg.SYSTEM_PROMPT)
    yield
    system_prompt.set(cfg.SYSTEM_PROMPT)


def test_get_returns_default_on_startup():
    assert system_prompt.get_base() == cfg.SYSTEM_PROMPT


def test_get_includes_examples_block():
    assert system_prompt.get().startswith(cfg.SYSTEM_PROMPT)
    assert system_prompt.get() != cfg.SYSTEM_PROMPT


def test_set_changes_the_prompt():
    system_prompt.set("Custom prompt")
    assert system_prompt.get_base() == "Custom prompt"
    assert system_prompt.get().startswith("Custom prompt")


def test_set_empty_string():
    system_prompt.set("")
    assert system_prompt.get_base() == ""


def test_multiple_sets_last_value_wins():
    system_prompt.set("first")
    system_prompt.set("second")
    assert system_prompt.get_base() == "second"
