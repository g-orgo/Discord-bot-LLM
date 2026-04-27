# Context - Benchmark and Default Model Update

Date: 2026-04-27

Summary:
- Executed benchmark with 10 local Ollama models to measure latency and objective response adherence.
- Selected qwen2.5:7b as new default model for the LLM service based on the best combined score.
- Added a second benchmark report for fine-tuning options and model-by-model recommendations.

Files created/modified:
- config.py: switched DEFAULT_MODEL from llama3.2:3b to qwen2.5:7b.
- README.md: updated setup/default model references and request/response examples.
- DECISIONS.md: updated default-model decision rationale based on benchmark.
- CLAUDE.md: updated local model pull command and DEFAULT_MODEL reference.
- .github/copilot-instructions.md: updated documented default model.
- benchmark_ollama_models.py: benchmark script for latency and objective adherence.
- benchmark_ollama_models.json: raw benchmark results for 10 models.
- benchmark_finetuning_options.py: estimator script for fine-tuning options.
- benchmark_finetuning_options.json: model-by-model fine-tuning benchmark output.
- BENCHMARKS_2026-04-27.md: consolidated benchmark report with explanations per model.

Decisions made:
- Adopt qwen2.5:7b as system default due to highest latency/quality score in this environment.
- Keep benchmark scripts and json outputs in repo for reproducibility and future reruns.
- Recommend QLoRA_4bit as first fine-tuning path for qwen2.5:7b.

Known issues or next steps:
- Fine-tuning benchmark is an engineering estimate (not a full training run) and should be validated with a pilot dataset.
- Re-run the benchmark after any hardware/runtime changes (Ollama version, host machine, model quantization).
