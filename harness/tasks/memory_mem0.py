"""Multi-session memory A/B: baseline (no memory) vs treatment (Mem0 retrieval).

Why a new executor
------------------
Memory is a *lifetime-leg* claim: it cannot be measured on a single-session
task, because the saving only appears when a later session would otherwise
re-ask or re-read. Each task in `tasks/memory_sessions.json` is therefore one
scenario: a sequence of sessions that share nothing but the memory store.

    baseline    each session is answered from its prompt alone
    treatment   Mem0 carries earlier sessions; what it retrieves is injected

Measurement surface: **tokens per scenario, summed over all sessions** — the
honest unit, and the one vendor token claims almost never state.

The bill includes the memory system's own extraction calls. Writing memory
spends LLM tokens, and a tool whose write cost eats its read saving is a
negative result, not a measured win. `answer_*` and `write_*` are recorded
separately in metadata so both sides of that arithmetic stay visible.

Quality guard: keyword checks per session (fraction passed). A memory arm that
retrieves the wrong fact fails the guard.

Three failure modes are recorded as data rather than being silently swallowed —
each one, unrecorded, produced a plausible-looking *false win* during
development: a retrieval that fails looks like a shorter prompt, and a store
that fails to write looks like zero write cost:

  - `retrieval_failures` — sessions where `search()` raised
  - `write_failures` — sessions where `add()` raised
  - `extraction_blocked` — the provider refused the extraction call (see the
    Groq TPM note in README.md); the arm then carries no memory at all

Answers and recalled memories are stored in metadata (truncated) so every
report can be audited without re-running it.

Requires:
    pip install "mem0ai" "fastembed"
    GROQ_API_KEY          free tier is fine for the answer channel
    MEM0_INFER=0          skip LLM extraction (raw store); see README

Cost basis: tokens are exact (tiktoken). `cost_usd` is computed at the repo's
existing proxy rate (Sonnet-5 list, tasks/example.py) so the delta is
comparable with the leaderboard; the actual Groq free-tier cost is $0.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from pathlib import Path

from token_harness.runner import TaskResult

MODEL_DEFAULT = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
EMBEDDER_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDER_DIMS = 384

# Same proxy rate as tasks/example.py — see module docstring.
PRICING = {"input": 3.0, "output": 15.0}

SYSTEM_BASELINE = "You are a helpful assistant. Answer the user's question."
SYSTEM_MEMORY_HEADER = (
    "You are a helpful assistant. Answer the user's question.\n\n"
    "Facts recalled from earlier sessions. Use them; do not invent beyond them."
)
MEMORY_TOP_K = 5
SNIP = 400  # metadata truncation for auditable answers/recalls


def _load_scenarios(tasks_path: str | Path) -> list[dict]:
    scenarios = json.loads(Path(tasks_path).read_text(encoding="utf-8"))
    if isinstance(scenarios, dict):
        scenarios = scenarios["tasks"]
    return scenarios


def _client(model: str):
    import openai

    return openai.OpenAI(api_key=os.environ.get("GROQ_API_KEY"), base_url=GROQ_BASE_URL)


def _chat(client, system: str, messages: list[dict], model: str):
    """One chat call. Returns (text, usage) with exact output token count."""
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, *messages],
        temperature=0,
        max_tokens=1024,
    )
    text = response.choices[0].message.content or ""
    usage = getattr(response, "usage", None)
    tokens_in = getattr(usage, "prompt_tokens", None)
    if tokens_in is None:
        # Exact count of everything sent, per the repo's counting rule.
        tokens_in = sum(len(enc.encode(m["content"])) for m in messages) + len(
            enc.encode(system)
        )
    return text, {"in": int(tokens_in), "out": len(enc.encode(text))}


class _Ledger:
    """Records usage from every LLM call made during a task.

    Mem0 builds its own client internally, so its extraction calls are captured
    by patching the OpenAI SDK rather than threading a client through it.
    """

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def record(self, kind: str, usage: dict) -> None:
        self.calls.append({"kind": kind, "in": usage["in"], "out": usage["out"]})

    def split(self) -> dict[str, int]:
        out = {"answer_in": 0, "answer_out": 0, "write_in": 0, "write_out": 0}
        for call in self.calls:
            if call["kind"] == "answer":
                out["answer_in"] += call["in"]
                out["answer_out"] += call["out"]
            else:
                out["write_in"] += call["in"]
                out["write_out"] += call["out"]
        return out


class _Channel:
    """Marks which channel the in-flight call belongs to."""

    def __init__(self) -> None:
        self._kind: str | None = None

    def set(self, kind: str) -> None:
        self._kind = kind

    def __call__(self) -> str | None:
        return self._kind


def _patch_openai_usage(ledger: _Ledger, channel: _Channel) -> None:
    """Wrap Completions.create so mem0's internal calls are metered."""
    import openai.resources.chat.completions as completions_mod

    original = completions_mod.Completions.create
    if getattr(original, "_token_harness_patched", False):
        return

    def patched(self, *args, **kwargs):
        response = original(self, *args, **kwargs)
        kind = channel()
        if kind is not None:
            usage = getattr(response, "usage", None)
            if usage is not None:
                ledger.record(
                    kind,
                    {
                        "in": int(getattr(usage, "prompt_tokens", 0) or 0),
                        "out": int(getattr(usage, "completion_tokens", 0) or 0),
                    },
                )
        return response

    patched._token_harness_patched = True
    completions_mod.Completions.create = patched


def _mem0_store(task_id: str, model: str, store_dir: str):
    """Build a Mem0 OSS store, isolated to this task's directory.

    Isolation is not tidiness: two scenarios sharing a vector collection can
    cross-contaminate retrieval, and a collection created under one embedder
    dimension cannot be read under another.
    """
    from mem0 import Memory

    extraction_model = os.environ.get("MEM0_EXTRACTION_MODEL", model)
    return Memory.from_config(
        {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": extraction_model,
                    "openai_base_url": GROQ_BASE_URL,
                    "api_key": os.environ.get("GROQ_API_KEY"),
                },
            },
            "embedder": {
                "provider": "fastembed",
                "config": {"model": EMBEDDER_MODEL},
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "path": str(Path(store_dir) / "qdrant"),
                    "collection_name": "memories",
                    "embedding_model_dims": EMBEDDER_DIMS,
                },
            },
            "history_db_path": str(Path(store_dir) / "history.db"),
            "version": "v1.1",
        }
    )


def _recall(store, prompt: str, task_id: str) -> tuple[list[str], str | None]:
    """Search the store. Returns (recalled strings, error message or None)."""
    try:
        hits = store.search(
            query=prompt, filters={"user_id": task_id}, limit=MEMORY_TOP_K
        )
    except Exception as exc:  # noqa: BLE001 - recorded as data, see docstring
        return [], f"{type(exc).__name__}: {exc}"[:SNIP]
    if isinstance(hits, dict):
        hits = hits.get("results", [])
    recalled = [h.get("memory", "") for h in (hits or []) if isinstance(h, dict)]
    return recalled, None


def _remember(store, task_id: str, prompt: str, answer: str) -> str | None:
    """Write the exchange to the store. Returns an error message, or None."""
    try:
        store.add(
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer},
            ],
            # v1.1: add() takes a top-level id; search() takes filters=.
            user_id=task_id,
            infer=os.environ.get("MEM0_INFER", "1") != "0",        )
        return None
    except Exception as exc:  # noqa: BLE001 - recorded as data, see docstring
        message = f"{type(exc).__name__}: {exc}"[:SNIP]
        return "EXTRACTION_BLOCKED" if "rate_limit_exceeded" in message else message


def _grade(scenario: dict, answers: list[str]) -> float | None:
    """Fraction of keyword checks passed. A session with no answer is a miss."""
    checks = scenario.get("checks", [])
    if not checks:
        return None
    passed = 0
    for check in checks:
        idx = check["session"] - 1
        answer = answers[idx].lower() if idx < len(answers) else ""
        groups = check["any_of"]
        if any(all(token in answer for token in group) for group in groups):
            passed += 1
    return passed / len(checks)


def run_task(task: dict, arm: str, model: str = MODEL_DEFAULT) -> TaskResult:
    """Run one multi-session scenario under one arm and meter the whole thing."""
    client = _client(model)
    ledger = _Ledger()
    channel = _Channel()
    _patch_openai_usage(ledger, channel)

    store_dir = tempfile.mkdtemp(prefix=f"mem0-{task['id']}-")
    store = None
    retrieval_failures: list[str] = []
    write_failures: list[str] = []
    try:
        if arm == "treatment":
            store = _mem0_store(task["id"], model, store_dir)

        answers: list[str] = []
        recalls: list[list[str]] = []
        start = time.monotonic()

        for i, session in enumerate(task["sessions"]):
            prompt = session["prompt"]

            recalled: list[str] = []
            if store is not None and i > 0:
                channel.set("answer")
                recalled, error = _recall(store, prompt, task["id"])
                if error:
                    retrieval_failures.append(f"session {i + 1}: {error}")

            system = SYSTEM_BASELINE
            if recalled:
                system = SYSTEM_MEMORY_HEADER + "\n\n" + "\n".join(
                    f"- {r}" for r in recalled
                )

            # History is cleared each session on purpose: a memory system that
            # needs the transcript carried forward is measuring the window.
            channel.set("answer")
            answer, usage = _chat(
                client, system, [{"role": "user", "content": prompt}], model
            )
            answers.append(answer)
            recalls.append(recalled[:MEMORY_TOP_K])
            ledger.record("answer", usage)

            if store is not None:
                channel.set("write")
                error = _remember(store, task["id"], prompt, answer)
                if error:
                    write_failures.append(f"session {i + 1}: {error}")

        wall_clock = time.monotonic() - start
    finally:
        shutil.rmtree(store_dir, ignore_errors=True)

    split = ledger.split()
    tokens_in = split["answer_in"] + split["write_in"]
    tokens_out = split["answer_out"] + split["write_out"]
    cost = (tokens_in * PRICING["input"] + tokens_out * PRICING["output"]) / 1_000_000

    metadata = {
        "model": model,
        "provider": "groq",
        "sessions": len(task["sessions"]),
        "tokenizer": "cl100k_base (proxy; model is not an OpenAI family model)",
        "cost_basis": "proxy at Sonnet-5 list rates; actual Groq free-tier cost $0",
        "retrieval_failures": retrieval_failures,
        "write_failures": write_failures,
        "answers": [a[:SNIP] for a in answers],
        "recalled": [[r[:SNIP] for r in r_] for r_ in recalls],
    }
    if arm == "treatment":
        metadata["memory"] = {
            "tool": "mem0ai",
            "version": _mem0_version(),
            "top_k": MEMORY_TOP_K,
            "extraction_model": os.environ.get("MEM0_EXTRACTION_MODEL", model),
            "infer": os.environ.get("MEM0_INFER", "1") != "0",
            "embedder": EMBEDDER_MODEL,
        }

    return TaskResult(
        task_id=task["id"],
        arm=arm,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost,
        wall_clock_s=wall_clock,
        quality_score=_grade(task, answers),
        metadata=metadata,
    )


def _mem0_version() -> str:
    try:
        import importlib.metadata

        return importlib.metadata.version("mem0ai")
    except Exception:  # noqa: BLE001
        return "unknown"
