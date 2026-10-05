# The Seven-Word Baseline That Beat Two Token-Saving Tools

*Why the cheapest intervention in a recent A/B test was a sentence — and what that means for every "AI-powered" token optimizer.*

---

Two tools. One harness. Three arms.

We put two popular token-saving tools through a paired A/B measurement — same tasks, same model, same Docker sandbox, real billed trials, significance tests. Then we added a third arm that cost nothing: a seven-word prompt.

## The contenders

| Arm | What it is | Advertised |
|---|---|---|
| **ponytail** | "The laziest senior dev" — rewrites code to be terse | −54% code, −20% cost |
| **caveman** | Output-side prose compression for Claude Code | −65% output tokens |
| **"Follow YAGNI, prefer one-liners"** | A seven-word system prompt | — |

## The results

| Arm | Code | Tokens | Cost | Time | Safe |
|---|---|---|---|---|---|
| `ponytail` | −54% | −22% | −20% | −27% | 100% |
| `caveman` | −20% | **+7%** | **+3%** | +2% | 100% |
| *"Follow YAGNI, prefer one-liners"* | −33% | −14% | −21% | −30% | 95% |

The seven-word prompt **matched ponytail on cost and time** while being free, instant, and model-agnostic. It was also the only arm that wrote an unsafe function — it dropped a path-traversal check once in four runs.

The cheapest intervention is often a sentence. But the cheapest intervention is not always the safest one.

## Why this matters

The gap between advertised and measured savings is the least-measured quantity in the entire field. Of three popular token tools put through one paired A/B harness:

- One delivered −8.5% against a −65% claim
- One was **more expensive** than baseline (+7.6% cost, p=0.004)
- One underdelivered on code size but did deliver on cost

Nobody knew in advance. That is why the grades exist.

## The methodology

```
model: claude-sonnet-5
harness: Claude Code 2.1.201 (headless, Docker-sandboxed)
date: 2026-07
n: 80 paired trials
quality: 65/80 identical outputs
significance: paired t-test, p < 0.05
```

Every number has a baseline, a method, and a stamp. Anything without one is `[self-reported]`, however large the number.

## The takeaway

Before you install a token-saving tool, ask: *what is the seven-word baseline?*

A prompt that says "prefer one-liners" costs nothing, loads in every context, and matches tools that claim −54%. The tools that beat it do so by a margin you should measure, not assume.

And if you run one of these tools yourself, publish the number. The gap between what a tool claims and what the bill says is currently the least-measured quantity in the entire field.

---

*This post is part of [awesome-token-minimalism](https://github.com/ranjithrajv/awesome-token-minimalism), an evidence-graded list of papers, tools, and patterns for spending fewer tokens on all three sides of an LLM call. Every entry carries a grade. Read the [token ledger](https://github.com/ranjithrajv/awesome-token-minimalism#token-ledger) before buying anything in the list.*
