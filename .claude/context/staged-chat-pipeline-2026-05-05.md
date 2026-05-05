# Date
2026-05-05

# Summary
Added discrete chat pipeline endpoints so the Discord bot can run linkedinfy, context gate, translation, and optional suggestion stages separately while keeping one visible interaction message updated.

# Files created/modified
- routes/chat.py: extracted stage helpers, updated `/chat` to the new primary order, and added `/chat/pipeline/*` endpoints for linkedinfy, context gate, translation, raw suggestions, and finalized suggestions.
- schemas.py: added request/response models for context gate and suggestion stages.
- tests/test_routes.py: updated `/chat` tests to the new staged helpers.
- README.md: documented the new staged endpoints and why they exist.

# Decisions made
- Kept `/chat` as a compatibility endpoint that returns only the primary final message.
- Exposed optional suggestion work as separate endpoints so the bot can stop early after translation and avoid unnecessary compute.
- Reused the same retry/error mapping for every stage to keep transient Ollama failures consistent.

# Known issues or next steps
- `/chat/stream` still follows its own streaming path and is not yet exposed as a fully staged streaming workflow.
- If other clients need the checkpoint behavior, they can build on the new `/chat/pipeline/*` endpoints without changing the bot contract.