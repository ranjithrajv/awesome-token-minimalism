# Agent Memory, Measured: Input Up, Output Down, Quality Up — and the Write Cost Nobody Bills

*Published 2026-10-13. Suite: `harness/tasks/memory_sessions.json` (12 scenarios × 3 sessions). Executor: `harness/tasks/memory_mem0.py`. Model: `openai/gpt-oss-120b` via Groq, temperature 0, 36 sessions per arm.*

**The finding:** A raw-store memory arm **more than doubles input tokens**
(+109.3%), cuts output by nearly three quarters (−73.5%), and improves
answer quality — for **−35.9% total tokens** against a paired no-memory
baseline (n=12, p<0.0001 on both token columns, p=0.027 on quality). The
headline a memory vendor would print is real but incomplete: it hides that
**input nearly doubled**, and it hides the extraction cost entirely, which in
this configuration is an **order of magnitude larger than the conversation it
serves**.

This is also a story about a false win. The first version of this measurement
produced a clean-looking −68 input / −2,040 output result that was entirely an
artifact of a broken retrieval path — the arm carried no memory and merely
answered shorter. It is in the list because of what it cost to find, not
because the artifact was interesting.

---

## The suite

`tasks/memory_sessions.json` — 12 scenarios, 3 sessions each. Session 1
establishes facts; sessions 2–3 are only answerable from session 1. Each
scenario carries keyword checks, so a retrieval that returns the *wrong* fact
fails the quality guard rather than looking like a shorter prompt.

The scenarios cover the cases where memory is load-bearing rather than
decorative: project stack and cadence, decisions *with their rationale*, hard
constraints ("never touch the legacy auth module"), an API contract, module
ownership, artifact paths, an ordered timeline, four similar numeric limits, and
a revert ("we tried this and it cost 180 ms of p99") where the superficially
attractive answer is the one already rejected.

Session 4 in `mem-revert-12` is the interesting one: the trap question has a
confident, obvious, already-disproven answer. Memory's value is concentrated in
the scenarios where plausible-and-wrong is the default.

## Method

| | |
|---|---|
| Unit | one scenario (3 sessions), summed |
| Arms | `baseline` (prompt alone) vs `treatment` (mem0 raw store, retrieval injected) |
| Pairing | both arms per scenario, paired t-test, 95% confidence |
| Counting | `tiktoken` `cl100k_base` (proxy — the model is not OpenAI-family) |
| Cost | Sonnet-5 list rates as a proxy; actual Groq free-tier cost is $0 |
| State | per-task store directory, deleted after each task |

History is cleared between sessions in both arms. A memory system that needs
the transcript carried forward is measuring the window, not the memory.

## Results

| Metric | Δ per scenario | 95% CI | p-value |
|---|---|---|---|
| tokens_in | **+399.25** | [+267.10, +531.40] | **<0.0001** |
| tokens_out | **−1,035.83** | [−1,284.01, −787.65] | **<0.0001** |
| cost_usd | −$0.01 | [−0.02, −0.01] | <0.0001 |
| wall_clock_s | −0.29 | [−2.62, +2.05] | 0.79 (ns) |
| **quality guard** | **+0.292** | [+0.040, +0.544] | **0.027** |

Totals across 12 scenarios: input 4,384 → 9,175 (**+109.3%**), output
16,919 → 4,489 (**−73.5%**), all tokens 21,303 → 13,664 (**−35.9%**). Mean
quality 0.667 → 0.958.

The mechanism behind the output drop is worth stating, because it is not
"memory makes the model terse." Without memory the baseline answered the
recall questions from pretraining — it explained that the service was written
in **Go**, then refused the database question entirely. With memory it answered
in one line, correctly. The output saved is the output that was previously
spent being confidently wrong.

| Scenario | baseline in/out | memory in/out | quality baseline → memory |
|---|---|---|---|
| mem-stack-01 | 672 / 1,129 | 609 / 115 | 0.00 → 1.00 |
| mem-constraints-04 | 333 / 1,750 | 1,035 / 1,487 | 0.50 → 1.00 |
| mem-owners-08 | 330 / 1,205 | 837 / 303 | 1.00 → 1.00 |
| mem-numbers-11 | 339 / 1,864 | 745 / 171 | 1.00 → 1.00 |
| mem-timeline-10 | 335 / 1,222 | 782 / 283 | 0.00 → 1.00 |
| mem-revert-12 | 332 / 1,682 | 866 / 403 | 0.50 → 0.50 |

`mem-revert-12` did not improve in either arm — the model still recommended the
previously reverted change. Memory retrieved the history; the model used it
anyway. Retrieval quality and decision quality are different measurements, and
this suite measures the first.

## What is not measured, and it is the larger half

The rows above are the **raw store** (`MEM0_INFER=0`): no extraction, retrieval
returns the stored exchanges verbatim. The flagship extraction path could not
run here. mem0 v1.1's extraction call requests:

| Model | Extraction call input tokens | Free-tier cap |
|---|---|---|
| `openai/gpt-oss-120b` | 8,802 | 8,000 TPM |
| `qwen/qwen3.8-27b` | 8,234 | 7,000 ITPM |
| `openai/gpt-oss-20b` | 8,160 | 8,000 TPM |

Every one returns `413 Request too large`. That size is a **fixed template
cost, not a payload effect** — a 60-character message and a 33,908-character
prompt. Arithmetic on a measured prompt size:

   36 add() calls × ~8,200 input tokens ≈ 295,000 tokens
   baseline conversation across the same 12 scenarios = 21,303 tokens

The write cost would be roughly **14× the conversation being remembered**. This
is a projection from a measured prompt, not a completed run, and it is the
single most important number to re-measure on a provider with ≥9k TPM headroom.
But it reframes the vendor claim completely: the −61.4% token figure that
accompanies tools in this family is a *read-side* number, and the read side is
the half that the extraction pipeline exists to serve.

## The false win, recorded

The first run of this executor reported **−68.5 input / −2,040.5 output
tokens**. Both numbers were artifacts:

- mem0 v1.1's `search()` requires `filters={"user_id": ...}`; a top-level
  `user_id` raises `ValueError`, and the failure was swallowed into a
  fallback path.
- with retrieval broken, the treatment arm's prompts were *shorter*, so the
  saving looked real.

The quality guard is what exposed it — the treatment arm's quality dropped to
0.00 on two scenarios — and the fix was to record retrieval and write failures
as first-class data in every report (`retrieval_failures`, `write_failures`,
`extraction_blocked`) rather than swallowing them. Every report now stores the
answers and the recalled memories, truncated, so a report can be audited
without re-running the experiment.

**A measurement that cannot fail is not a measurement.** The runner now
distinguishes "no memory was found" from "memory was not asked for."

## Honest limits

- **n=12, one model, one harness, one day.** Directional, not conclusive.
- **Raw store, not the flagship path.** Verbatim recall flatters retrieval;
  extraction compresses and would change both columns.
- **Single-turn sessions.** No tool calls, no agent loop, no prompt cache — and
  the [interaction matrix](../README.md#interaction-matrix) says a cache miss on
  the injected prefix is where this trade gets decided.
- **Keyword checks** measure recall, not correctness of use.
- **Proxy tokenizer and proxy cost rate**; absolute totals carry that
  approximation.

## Re-run it

```sh
cd harness
pip install -e ".[dev]" && pip install "mem0ai" "fastembed"
env -u HF_TOKEN MEM0_INFER=0 \
  token-harness run --tasks tasks/memory_sessions.json \
  --config configs/mem0-groq.json --output report.json
```

To measure the extraction arm, point `MEM0_EXTRACTION_MODEL` at a provider with
≥9k TPM headroom; the executor already separates answer and write channels.

---

*Part of [awesome-token-minimalism](https://github.com/ranjithrajv/awesome-token-minimalism).*
