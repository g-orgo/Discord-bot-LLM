# Date
2026-05-05

# Summary
Switched the operational default Ollama model from qwen2.5:7b to qwen2.5:1.5b to reduce RAM usage and improve response latency while keeping acceptable output quality for the project workflow.

# Files created/modified
- config.py: changed DEFAULT_MODEL fallback to qwen2.5:1.5b.
- README.md: updated setup and env var docs to the new default model.
- OPERATIONS_GUIDE.md: updated env var table, production env example, and troubleshooting pull command.
- DECISIONS.md: recorded the 2026-05-05 default-model decision update.
- .github/copilot-instructions.md: updated local dev pull command and default model reference.
- CLAUDE.md: updated local pull command and DEFAULT_MODEL description.

# Decisions made
- Adopt qwen2.5:1.5b as the default model due to significantly lower RAM usage and lower benchmark latency than qwen2.5:7b in the current environment.
- Keep qwen2.5:7b available as a fallback option when stricter adherence is required.

# Known issues or next steps
- Some prompt-adherence drift was observed in qwen2.5:1.5b on specific rewrite cases; monitor production outputs.
- If adherence is unacceptable, either tune prompt constraints/guardrails or revert DEFAULT_MODEL to qwen2.5:7b.
