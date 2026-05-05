"""
Loads training examples from training/ subfolders and builds few-shot context.

- training/raptor/   → brand/communication examples (used by /chat system prompt)
- training/translate/ → translation examples (used by /translate endpoint)
"""
import json
from pathlib import Path

_BASE_DIR = Path(__file__).parent / "training"


def load_examples() -> str:
    """Return a formatted few-shot block from training/raptor/, sorted by filename."""
    training_dir = _BASE_DIR / "raptor"
    if not training_dir.exists():
        return ""

    examples: list[str] = []
    for path in sorted(training_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            user_req = data.get("user_request", "").strip()
            expected = data.get("expected_output", "").strip()
            if user_req and expected:
                examples.append(f'Input: "{user_req}"\nOutput: "{expected}"')
        except Exception:
            pass

    if not examples:
        return ""

    block = "\n\n".join(examples)
    return f"\n\nHere are reference examples of correct transformations:\n\n{block}"


def load_translate_examples(max_examples: int | None = None) -> str:
    """Return a formatted few-shot block from training/translate/, sorted by filename."""
    training_dir = _BASE_DIR / "translate"
    if not training_dir.exists():
        return ""

    examples: list[str] = []
    for path in sorted(training_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            inp = data.get("input", "").strip()
            out = data.get("output", "").strip()
            if inp and out:
                examples.append(f'Input: "{inp}"\nOutput: "{out}"')
        except Exception:
            pass

        if max_examples is not None and max_examples > 0 and len(examples) >= max_examples:
            break

    if not examples:
        return ""

    block = "\n\n".join(examples)
    return f"\n\nExamples:\n\n{block}"
