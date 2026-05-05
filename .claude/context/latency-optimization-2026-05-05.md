# Date
2026-05-05

# Summary
Executed end-to-end latency benchmarks for /chat and /benchmark, then applied low-risk changes to reduce average response time. Main strategy: reduce expensive multi-pass chat post-processing by default and switch default model to qwen2.5:7b.

# Files created/modified
- config.py: switched DEFAULT_MODEL to qwen2.5:7b; added CHAT_ENABLE_CONTEXT_GATE and CHAT_MIN_ALTERNATIVES env flags.
- routes/chat.py: made context-gate/regeneration optional via config flags to reduce extra LLM calls per request.
- routes/benchmark.py: added model, warmup_runs, and message query params plus options/warmup metadata in response.
- README.md: documented updated defaults, performance flags, and benchmark endpoint parameters.
- .claude/context/latency-optimization-2026-05-05.md: recorded benchmark results and decisions.

# Decisions made
- Kept translation preprocessing in /chat for behavior consistency; optimized by defaulting off expensive post-processing.
- Set qwen2.5:7b as default because measured /chat latency was consistently lower than llama3.2:3b in this environment.
- Added benchmark query params so model comparisons no longer require code edits.

# Benchmark snapshot
Before changes (/chat, 3 runs after warmup, same prompt):
- llama3.2:3b avg: 4768.6 ms
- qwen2.5:7b avg: 2000.0 ms

After changes (/chat, 5 runs after warmup, same prompt):
- llama3.2:3b avg: 1653.1 ms (median 1663.2 ms)
- qwen2.5:7b avg: 1303.6 ms (median 1315.6 ms)

After changes (/benchmark, runs=5, warmup_runs=1, same message):
- llama3.2:3b avg_request_ms: 1046.5, avg_tokens_per_second: 112.6
- qwen2.5:7b avg_request_ms: 1138.4, avg_tokens_per_second: 61.0

# Known issues or next steps
- pytest is not available in the current shell environment (CommandNotFoundException); install test dependencies before running the test suite.
- /benchmark measures one direct Ollama chat call, while /chat includes translation + rewrite flow; choose model using /chat numbers for product impact.
