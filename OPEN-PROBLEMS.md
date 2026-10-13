# Open problems

> **The gaps, kept on purpose.** Every section of the list rests on evidence;
> these are the places where there is none. Nobody has measured them, and
> saying so is cheaper than guessing.

Part of [Awesome Token Minimalism](README.md).

---

## Contents

- [The sixteen questions](#the-sixteen-questions)
- [See also](#see-also)

---

## The sixteen questions

Real gaps, numbered so they can be cited. Each one states enough of the
shape of the answer that someone could go get it. Answering one outranks
any number you could add to an existing section.

### 1. Where does a retention bar stop being worth its tokens?

test-audit's retention bar is prose in a skill: it costs tokens on every run and slows every deletion. Obviously worth it at 400k LOC. Where's the threshold?

### 2. Is there a quality-preserving minimum for any artifact?

ponytail and CoD both found *accuracy rising* as output shrank. Is there a floor, and how do you know you've hit it without a benchmark?

### 3. Does lifetime bloat compound?

If token 3 of a test file costs more than token 1 (because later tokens only get read when the first fails), the lifetime curve isn't linear and every deletion decision changes.

### 4. What is the *correct* unit for compression loss?

tokens-per-task is better than tokens-per-request, but it requires knowing the re-fetch rate, which is unmeasured almost everywhere.

### 5. Which context-window profiler is independently audited, and by what diff?

Most of [Leg 0](README.md#leg-0--measure) is `[self-reported]`; the `[measured]` entries audit instruction files and bills, not per-turn context composition. This repo now ships a baseline — [`token-harness profile`](harness/docs/context-profiler.md), which reads an agent's own event stream and reports the window turn by turn — so the question is no longer whether one exists but **which third-party profiler agrees with it, and where the boundaries differ.** [`contextlens-profiler`](https://pypi.org/project/contextlens-profiler/) is the candidate: listed `[measured]` here, describing exactly this capability, so either the entry is graded generously or the question was wrong. An audit is a diff, not an opinion.

### 6. Is per-model brevity tuning worth it?

Verbosity compensation suggests conciseness is model-specific. Whether one ruleset can serve three model families, or needs to be three rulesets, is unmeasured.

### 7. Does bounded-goal cleanup invite reward hacking at scale?

The 400k number came with a coverage guard that coverage-gaming could satisfy.

### 8. What is the break-even query volume for a graph index?

ContextRAG says it is "most attractive for low- and medium-query workloads, especially when corpora are re-indexed frequently" — but nobody has published the curve. You would need `index_cost / (per_query_vector_saving × queries)` against corpus churn, and no framework reports the first term by default. GraphRAG's own indexing-cost tracking was a [user feature request](https://github.com/microsoft/graphrag/issues/1153), not a default.

### 9. Is graph structure or extraction the thing that matters?

ContextRAG and TERAG both drop LLM-written edges and keep the graph, with large token wins. Nobody has cleanly separated "structure helps retrieval" from "LLM-written structure is expensive," which is why the token column and the relevance column disagree so consistently across the [table above](README.md#%F0%9F%95%B8%EF%B8%8F-graph-engineering).

### 10. Where is the delete↔cache crossover?

Context editing wins on tokens *and* performance in Anthropic's own eval, but clearing invalidates the prefix — and nobody has published hit rate *before and after* enabling it. Without that pair of numbers, "should we turn on context editing?" has no evidence-based answer outside one vendor's internal benchmark.

### 11. Is there a hit rate above which preloading always wins?

CAG is ~10–17× faster at query time but needs *more* resident memory (18GB vs 12GB on HotpotQA) and a corpus stable enough to precompute. Break-even depends on query volume, corpus churn, and hit rate simultaneously — three variables, no published curve.

### 12. Semantic caching is deliberately absent

It saves more than any mechanism in this list and it is the one most likely to return a confidently wrong answer. Omitted rather than uncritically included; somebody should measure its false-hit rate.

### 13. What is the energy per query for a non-autoregressive decision model?

Every energy figure here is per-query at autoregressive inference. System One models remove the sequential decode loop, so they should be dramatically lower — but nobody has published a Wh/query for one, and the architecture is the whole reason to expect a difference. **"It should be much lower" is not a measurement**, and this is currently the largest unquantified claim the model-class argument rests on. → [Decide, don't generate](README.md#%F0%9F%8E%AF-decide-dont-generate)

### 14. Does the input side get cheaper too, or only the output side?

A decision model still reads the full state and still has a token budget (`head_max_len`), but it has no KV cache to reuse across turns and no prefix to cache. Whether that makes it better or worse than a cached LLM prefix for high-volume, repeated-state workloads is unmeasured — and it is exactly the case where the LLM's 0.1× cache read might win.

### 15. What is the independently measured token delta of codemod-versus-agent editing?

Everything in [Leg 2 — Output](README.md#leg-2--output) is either an author's characters-per-token *estimate*, a third party's un-reproduced percentage, or a vendor's own benchmark. The one genuine pair of numbers — an agent alone at **>65M tokens** against an agent calling recipes at **~30k**, Java 25 — is vendor-published for a vendor platform, with no stated task set and no replication. What would settle it: the same corpus, the same transform, a tokenizer over *both* arms, an independent harness, and the per-file re-read cost a long session imposes — the term every estimate omits. The 45/40–60/80% figures are conversion *rates*, not token counts, and nothing converts between them.

### 16. What does an authoring gate prevent, in tokens?

test-audit's first mechanism is an **authoring gate** — four questions before adding a test, where a missing answer means don't add it yet. It is the only *preventive* mechanism in Leg 3 and the only one with no number: the campaign mode has ~400k LOC (maintainer report, no n, no baseline), and the gate has nothing. You cannot count a token that was never spent, so this has to be measured as a difference — matched branches, one gated and one not, metered over both — and nobody has. The post that popularized it ([`@steipete`, 2026-09-24](https://x.com/steipete/status/2103147927313199260)) reports the *deletion*, which is the half that already has a number. Until the gate is metered, "don't write it" is the unmeasured half of a measured pair. → [Prune what you already emitted](README.md#%F0%9F%A7%B9-prune-what-you-already-emitted)

---

## See also

- [Awesome Token Minimalism](README.md) — the list proper
- [Anti-patterns](ANTI-PATTERNS.md) — the defaults that shipped unmeasured, with receipts
- [Token ledger](README.md#token-ledger) — advertised vs. independently measured
- [Token Maxxing](TOKENMAXXING.md) — the negative-result catalog
- [Break-even](README.md#%F0%9F%A7%AE-break-even) — the arithmetic that settles these

