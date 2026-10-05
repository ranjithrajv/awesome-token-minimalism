# Glossary

Terms this list uses precisely, because imprecise usage is how a cache gets
called a compressor. Alphabetical. Each entry gives the definition **and the
number that makes it matter**, where one exists.

Part of [Awesome Token Minimalism](README.md).

---

**Attention budget** — The finite capacity a transformer spends relating tokens
to each other. Every token added depletes it, whether or not the token is
useful. Arises from the architecture: *n* tokens create n² pairwise
relationships, so relationships per token thin out as context grows. The reason
"more context" is not free even when the window is.
→ [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Bloat** — Any token in the request, the response, or the artifact **whose
cost has not been measured against its contribution**. Not a synonym for
"large": a 1M-token window holding 40k of high-signal context is lean. Bloat is
a property of the *decision*, not the size.

**Bounded goal** — Replacing an open-ended optimization instruction ("be
concise", "clean up the tests") with a measured target plus a guard metric
("remove 20%, hold coverage within 2%"). Open-ended goals are systematically
**undershot**; over-tight ones are **overshot**. Both are fixed by bounding.
→ [Law 18](README.md#laws)

**Cache hit rate** — Fraction of input tokens served from cache rather than
recomputed. `cachedContentTokenCount` (Gemini) / `usage.cache_read_input_tokens`
(Anthropic). **The primary metric for any caching work** — cached vs uncached
is roughly a 10× price difference, so this single number moves more money than
any prompt edit.
→ [Leg 1 · Cache](README.md#%F0%9F%92%BE-cache)

**Cache write / cache read** — The two prices on a prefix cache. Writing costs
a premium (Anthropic: 1.25× base input); reading costs a discount (0.1×). The
write is repaid by **one** subsequent hit at a 90% hit rate, which is why the
write premium is not the thing to worry about — invalidation is.

**CAG (Cache-Augmented Generation)** — Precomputing a corpus's KV states offline
once, then answering queries against the cache with no retrieval step. ~10–17×
faster generation than no-cache on HotpotQA, at the cost of permanent resident
memory (18GB vs 12GB for sparse RAG).
→ [Leg 1 · Cache](README.md#%F0%9F%92%BE-cache)

**Compaction** — Replacing a span of conversation with a model-written summary.
Lossy by construction. Distinct from *deletion* (which drops content outright)
and from *retrieval* (which relocates it). Claude Code triggers it near 94–96%
of the window; the API default is 250k tokens.

**Context collapse** — Degradation where repeatedly rewriting/compacting context
causes the model to lose accumulated detail across generations. The reason
incremental structured updates beat wholesale rewrites for long-lived memory.

**Context editing** — *Provider-side* deletion of stale content, triggered by a
threshold. Anthropic: `clear_tool_uses_20250919` and
`clear_thinking_20251015`, default trigger 100k input tokens. Measured at +29%
agentic-search performance alone and −84% tokens on a 100-turn eval — but it
**invalidates the prefix cache** when the cleared content is in the prefix.
→ [Leg 1 · Delete](README.md#%F0%9F%97%91%EF%B8%8F-delete)

**Context engineering** — Curating what occupies the window at each step,
as distinct from *prompt engineering* (composing one instruction). A subset
relationship, not a replacement: prompt engineering is one input to context
engineering.

**Context rot** — Measurable degradation as input length grows, **before** any
stated context limit. Tested across 18 frontier models; all degraded, and
distractors have non-uniform impact. The empirical basis for the whole Input
leg.
→ [Chroma, 2025](https://research.trychroma.com/context-rot)

**Distractor** — Irrelevant context included alongside relevant context. Not
neutral padding: as input grows, distractors degrade performance *more*, and
some distractors cost far more attention than others.

**Effective context length** — The length at which a model still performs
reliably, as opposed to its advertised maximum. GPT-4-1106 claims 128K and
manages 64K; Llama3.1-70B falls off after 64K. Near-perfect needle-in-a-haystack
scores are not evidence of it.
→ [RULER (NVIDIA)](https://github.com/NVIDIA/RULER)

**Energy per query** — Watt-hours consumed serving one request. Frontier-scale
inference: median **0.31 Wh** (IQR 0.16–0.60), which is 4–20× *below* most
published estimates because those assume non-production deployments. Scales with
**output length, not task complexity** — output tokens are generated
sequentially while input tokens are processed in parallel. A reasoning query at
~5,000 output tokens runs **~13×** a standard one; DeepSeek-R1 measured
**20.9 Wh/query** against 0.21 Wh conventional.
→ [Joule / Microsoft Research](https://www.cell.com/joule/fulltext/S2542-4351%2826%2900114-5)

**Evidence grade** — The four-value vocabulary every entry in this list carries:
`[measured]`, `[self-reported]`, `[asserted]`, `[negative]`. `[measured]`
requires a baseline and a method; a number without a baseline is
`[self-reported]` however large.

**Just-in-time retrieval** — Holding lightweight *identifiers* (file path, query,
URL) and loading the payload only when the task needs it, rather than
pre-fetching all plausible context. The mechanism behind progressive disclosure.

**KV cache** — The stored key/value tensors from a transformer's attention
layers. Provider-managed KV reuse across requests is what "prompt caching"
means in practice. Precomputing it offline is CAG.

**Lifetime tokens** — The third leg: tokens emitted into an artifact become
context that **every future session** must read, grep, or reason over. A test
file is not paid for once; it is paid for every time anyone touches that
subsystem. The leg with no dashboards.
→ [Leg 3](README.md#leg-3--lifetime)

**MinAns / Irrel** — The two-part taxonomy of a model response: **minimal
answer** tokens (the actual answer) versus **irrelevant** tokens (hedging,
restating, hallucinated drift, repetition). Framing a prompt as "give the MinAns
only" measured ≈60% output reduction on its own.
→ [Brevity is the soul of sustainability (ACL 2025)](https://aclanthology.org/2025.findings-acl.1125/)

**Multimodal token** — Tokens charged for non-text input. Images, PDFs, audio,
and video are tokenized by dimension or duration, not by file size. A 1MP image
is ~1,334 tokens on Claude, ~765 on GPT-4o high-detail, ~258 on Gemini — a
~5× spread for the same pixels.
→ [Leg 1 · Multimodal](README.md#%F0%9F%96%BC%EF%B8%8F-multimodal-tokens)

**Prefix cache** — Provider-side reuse of the computed state of an identical
prompt prefix. Only works on exact, byte-identical prefixes, in ~1k-token
blocks. Saves 45–80% of cost and 13–31% of TTFT; killed by a timestamp or a
request ID in the system prompt.
→ [Don't Break the Cache](https://arxiv.org/html/2601.06007v1)

**Progressive disclosure** — Loading information in tiers as needed: a small
always-present catalog (a skill's name and description, ~100 tokens), the body
on activation (<5k tokens), and bundled files or scripts only when referenced
(no token cost until read). The same idea as just-in-time retrieval, applied to
instructions.
→ [Agent Skills spec](https://agentskills.io/)

**Prompt compression** — Reducing the token count of a prompt before sending it,
by token-level filtering (LLMLingua, up to 20×), summarization, or paraphrase.
⚠️ Compression **rewrites the prefix**, so it and caching are antagonistic —
see [Break-even](README.md#%F0%9F%A7%AE-break-even) for the threshold.
→ [Leg 1 · Compress](README.md#%E2%9C%82%EF%B8%8F-compress)

**Reasoning token** — Internal deliberation tokens in a reasoning model. Billed
at the **output** rate (the expensive one — often 5× input) and usually not
broken out on any dashboard. They can exceed 80% of total output cost while the
visible response is unchanged.
→ [Leg 2 · Audit](README.md#%F0%9F%93%90-audit)

**Retention bar** — The explicit list of things a deletion pass must **never**
remove (public API, protocol, migration, security, release contracts, regressions
with credible failure modes). A deletion without one is a regression with extra
steps.
→ [test-audit](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md)

**Semantic caching** — Reusing a *whole answer* for a semantically similar
query, bypassing the model run entirely. Saves the most of any mechanism here,
and carries the failure mode nobody measures: a confidently wrong answer.
Deliberately absent from this list's recommended entries until its false-hit
rate is published.

**Token ledger** — This list's table of advertised-versus-independently-measured
claims. Four popular tools, none hitting its headline, one more expensive than
doing nothing. The reason the evidence grades exist.
→ [Token ledger](README.md#token-ledger)

**Water footprint** — Litres consumed in cooling, per query. A short LLM session
can indirectly draw **~0.5 L** of fresh water; global data centres consumed
~**4.5 trillion litres** in 2025. Rarely reported by providers and almost never
allocated per workload, which is why it appears here as context rather than as
an optimization target.
→ [How Hungry is AI?](https://arxiv.org/html/2505.09598v6)**Tokens-per-task** — Total tokens consumed from task start to completion,
**including re-fetching caused by earlier over-compression**. The correct
optimization target; tokens-per-request is the naive one that rewards losing
information you later pay to recover.
→ [Law 21](README.md#laws)

**Verbosity compensation** — A model generating extra tokens to hedge or fill
uncertainty. Notably, **training toward brevity makes it worse**, not better —
distilling toward conciseness cut the behaviour from 63.8% to 16.6% frequency.
Brevity can be a training artifact, not a prompt property.
→ [UncertaiNLP 2025](https://aclanthology.org/2025.uncertainlp-main.13/)

**Visual token** — The unit of image cost. Claude: one token per 28×28-pixel
patch, `⌈w/28⌉ × ⌈h/28⌉`, capped at 1,568 (standard tier) or 4,784
(high-resolution tier). OpenAI: 85 base + 170 per 512×512 tile, flat 85 at
`detail: low`. Gemini: 258 flat under 384px, otherwise 258 per 768×768 tile.
→ [Leg 1 · Multimodal](README.md#%F0%9F%96%BC%EF%B8%8F-multimodal-tokens)

---

## Corrections

If a definition here is wrong or has gone stale, that is a high-value PR —
these terms are load-bearing for everything else in the list. Price ratios and
tokenization rules change with model releases; the definitions should not.
