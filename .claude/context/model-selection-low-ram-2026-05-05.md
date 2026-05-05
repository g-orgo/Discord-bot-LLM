# Model selection for low RAM (2026-05-05)

## Goal
Find a model with lower RAM usage and faster responses than qwen2.5:7b for /chat.

## Installed model sizes (ollama list)
- qwen2.5:7b -> 4.7 GB
- qwen2.5:1.5b -> ~1.0 GB pulled
- qwen2.5:0.5b -> 397 MB
- llama3.2:3b -> 2.0 GB
- dolphin-phi:latest -> 1.6 GB
- phi:latest -> 1.6 GB
- orca-mini:latest -> 2.0 GB

## Benchmark endpoint results (/benchmark, runs=4)
Prompt: "Translate to natural English: Precisamos pausar o projeto esta semana."

- qwen2.5:0.5b: avg_request_ms 432.3, avg_tps 316.3
- dolphin-phi:latest: avg_request_ms 435.6, avg_tps 119.0
- orca-mini:latest: avg_request_ms 602.8, avg_tps 72.8
- phi:latest: avg_request_ms 884.4, avg_tps 123.8
- llama3.2:3b: avg_request_ms 948.5, avg_tps 86.7
- qwen2.5:7b: avg_request_ms 985.9, avg_tps 65.2
- qwen2.5:1.5b: avg_request_ms 357.9, avg_tps 179.1

## Quick quality check (/chat)
- qwen2.5:7b: good adherence to current system prompt and expected rewriting behavior.
- qwen2.5:0.5b: fastest among existing small models, but failed instruction adherence in PT prompts.
- dolphin-phi / orca-mini / llama3.2:3b: frequent meta outputs and code-like artifacts, poor fit.
- qwen2.5:1.5b: very fast, but mixed adherence (some prompts produced structured notes or extra explanation).

## Practical recommendation
1) Keep qwen2.5 family for alignment with current prompt style.
2) Move default from qwen2.5:7b to qwen2.5:1.5b for major RAM reduction and large latency gain.
3) If instruction drift is unacceptable in production, keep qwen2.5:7b and instead tune latency knobs (NUM_PREDICT/NUM_CTX/keep_alive).
4) Do not use qwen2.5:0.5b as default without additional guardrails or prompt redesign.
