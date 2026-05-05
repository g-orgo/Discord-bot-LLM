# Context: Ollama Timeout Resilience

**Date:** 2026-05-04

## Summary
Adjusted the Ollama client timeout behavior in the LLM service after `/chat` requests were failing with `httpx.ReadTimeout` while the Ollama runner was still starting. Also skipped the translation validation pass when the input is already English to reduce avoidable model calls.

## Files created/modified

### Modified:
- `config.py` — raised the default `OLLAMA_TIMEOUT` from 60s to 300s
- `ollama.py` — switched from a single global timeout value to phase-specific `httpx.Timeout` settings with a longer read timeout
- `translation.py` — returns early from `translate_with_context_validation()` when translation output matches the original message
- `main.py` — added a FastAPI exception handler that maps `httpx.TimeoutException` to HTTP 504 with a clear diagnostic message
- `.github/copilot-instructions.md` — updated the documented meaning/default for `OLLAMA_TIMEOUT`

## Decisions made
- Kept the timeout configurable through the existing `OLLAMA_TIMEOUT` env var instead of introducing a second env var for read timeout.
- Used a longer read timeout because the observed failure happened while waiting for the Ollama runner/model to become ready, not during connection setup.
- Avoided changing the translation pipeline semantics for non-English input; only the redundant validation call for unchanged text was skipped.

## Known issues or next steps
- `/chat` can still be slower on very constrained hardware due to translation + generation calls; very slow environments may still need a larger `OLLAMA_TIMEOUT`.
- If latency remains high, the next optimization target is reducing prompt complexity or model size for the chat path.

---

## Update (same date)

### Summary
Implemented a second-pass context gate in the chat route to enforce that returned alternatives remain faithful to the original message intent and contain no meta labels/explanations.

### Files modified
- `routes/chat.py`
	- Added `_CONTEXT_GATE_SYSTEM` with strict rules for third-party voice, key-fact preservation, and meta-text removal.
	- Added `_context_gate_response(...)` to re-validate and clean model output before returning it in `/chat`.

### Decisions made
- Accepted an extra model pass for stronger output fidelity, prioritizing suggestion quality over latency.
- Kept API schema unchanged (`{ model, response }`) to avoid cross-service contract changes.

### Known issues or next steps
- Since this adds one extra call per `/chat`, latency may increase; if needed, add a feature flag to toggle context gate strictness by environment.

---

## Update (same date, minimum suggestions)

### Summary
Added a minimum-alternatives guard so `/chat` returns at least 2 valid options for downstream Discord suggestion buttons.

### Files modified
- `routes/chat.py`
	- Added `_count_or_alternatives(...)` to detect how many alternatives are present.
	- Added `_FORCE_ALTERNATIVES_SYSTEM` and `_ensure_min_alternatives(...)` to regenerate 2-3 alternatives when output has fewer than 2.
	- Updated `/chat` flow to run: generation -> context gate -> minimum alternatives check -> context gate.

### Decisions made
- Prioritized UX requirement (minimum 2 suggestions) over latency in this path.
- Kept response format unchanged (single `response` string with `Or` separators) to preserve bot compatibility.

---

## Update (same date, latency optimization)

### Summary
Optimized `/chat` flow to reduce Ollama calls from 4 per request down to 2-3 maximum by inlining alternatives logic.

### Files modified
- `routes/chat.py`
  - Inlined the alternatives check into the main `/chat` route logic.
  - Removed duplicate context gate calls and the `_ensure_min_alternatives` function.
  - Simplified flow: generation → gate → (if <2 alternatives) regenerate alternatives → gate once.

### Known issues or next steps
- If latency is still unacceptable on hardware <4GB RAM, next optimization is reducing system prompt complexity or switching to a smaller model.