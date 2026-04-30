import time
from fastapi import APIRouter, Query
from pydantic import BaseModel
from config import OLLAMA_CHAT_URL, DEFAULT_MODEL
from ollama import _get_client, _OLLAMA_OPTIONS
import system_prompt

router = APIRouter()

_BENCHMARK_MESSAGE = "Hi"


class BenchmarkRun(BaseModel):
    request_ms: float
    ollama_total_ms: float
    load_ms: float
    prompt_eval_ms: float
    gen_ms: float
    tokens_generated: int
    tokens_per_second: float


class BenchmarkResponse(BaseModel):
    model: str
    runs: int
    results: list[BenchmarkRun]
    avg_request_ms: float
    min_request_ms: float
    max_request_ms: float
    avg_tokens_per_second: float


@router.get("/benchmark", response_model=BenchmarkResponse)
async def benchmark(runs: int = Query(default=3, ge=1, le=10)):
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt.get()},
            {"role": "user", "content": _BENCHMARK_MESSAGE},
        ],
        "stream": False,
        "keep_alive": -1,
        "options": _OLLAMA_OPTIONS,
    }

    results: list[BenchmarkRun] = []
    client = _get_client()

    for _ in range(runs):
        t0 = time.perf_counter()
        res = await client.post(OLLAMA_CHAT_URL, json=payload)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        res.raise_for_status()
        data = res.json()

        load_ms = data.get("load_duration", 0) / 1e6
        prompt_eval_ms = data.get("prompt_eval_duration", 0) / 1e6
        gen_ms = data.get("eval_duration", 0) / 1e6
        total_ms = data.get("total_duration", 0) / 1e6
        eval_count = data.get("eval_count", 0)
        tps = eval_count / (gen_ms / 1000) if gen_ms > 0 else 0.0

        results.append(BenchmarkRun(
            request_ms=round(elapsed_ms, 1),
            ollama_total_ms=round(total_ms, 1),
            load_ms=round(load_ms, 1),
            prompt_eval_ms=round(prompt_eval_ms, 1),
            gen_ms=round(gen_ms, 1),
            tokens_generated=eval_count,
            tokens_per_second=round(tps, 1),
        ))

    request_times = [r.request_ms for r in results]
    tps_values = [r.tokens_per_second for r in results]

    return BenchmarkResponse(
        model=DEFAULT_MODEL,
        runs=runs,
        results=results,
        avg_request_ms=round(sum(request_times) / len(request_times), 1),
        min_request_ms=round(min(request_times), 1),
        max_request_ms=round(max(request_times), 1),
        avg_tokens_per_second=round(sum(tps_values) / len(tps_values), 1),
    )
