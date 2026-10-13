# Anti-patterns

> **Each one names a default that shipped unmeasured, with a receipt.**
> The enemy is never the capability — it is the cost nobody priced.

Part of [Awesome Token Minimalism](README.md).

> The same defaults appear as graded cases in
> [Token Maxxing](TOKENMAXXING.md#the-cases); this file is the index, that
> one the catalog.

---

## Contents

- [The nineteen defaults](#the-nineteen-defaults)
- [See also](#see-also)

---

## The nineteen defaults

### 1. Eagerly-loaded tool schemas

`tools/list` is a flat payload injected every turn; no partial-loading primitive exists in the spec, so every workaround lives above it. [GitHub MCP: 91 tools, ~17.6k tokens/session](https://www.atlassian.com/blog/developer/mcp-compression-preventing-tool-bloat-in-ai-agents). *Worst single tool observed: 557,766 average output tokens; 16 tools exceed 128k* ([MSR](https://www.microsoft.com/en-us/research/blog/tool-space-interference-in-the-mcp-era-designing-for-agent-compatibility-at-scale)).

### 2. Uncleared tool results

A turn-3 result still costing 8k tokens at turn 20.

### 3. Invisible reasoning spend

7.2× total call cost, unchanged visible response, no line item on the dashboard.

### 4. Uniform reasoning budgets

Thinking enabled on 100% of calls when ~60% don't need it — 40–70% of the output bill, wasted.

### 5. Duplicated instruction files

The same three rules pasted into `CLAUDE.md`, `.cursor/rules`, and `copilot-instructions.md`, loaded every turn. Measure the overlap, not just the total.

### 6. Whole-file rewrite as default

Robust and expensive, chosen without conditioning on scope. Cost is real; so is the whitespace-mismatch failure.

### 7. Dump-and-read retrieval

Raw output into context where `jq` or `--stat` would do.

### 8. N× self-consistency sampling

An accuracy method that multiplies the most expensive resource. Measure the marginal gain per sample.

### 9. Unrouted vector-only retrieval

No rerank, no citations, no audit trail. Also see the [RAG-is-dead roundup](https://www.forbes.com/councils/forbestechcouncil/2026/07/09/rag-didnt-die-it-moved-up-the-stack) — retrieval moved up the stack; stuffing pays ~1000× for degraded recall.

### 10. Unbounded background agents

14 agents × ~80k tokens, zero usable output ([claude-code #25714](https://github.com/anthropics/claude-code/issues/25714)). Needs a `remaining_context − (est_results × n_agents) > margin` check before launching.

### 11. Test bloat

Models over-test every tiny change. See [Leg 3](README.md#leg-3--lifetime) — and note that commit history is the audit trail.

### 12. Savings counters treated as evidence

`rtk` reported 99.8% savings while the bill rose. Only the bill counts.

### 13. GraphRAG-global as the default answer to "we need better retrieval."

**331,375 average prompt tokens** against vector RAG's 879, and it scales with corpus size — 7,800 → 40,000 as query difficulty rises ([arXiv 2506.05690](https://arxiv.org/html/2506.05690v3)). The capability being added is answering dataset-wide questions. The cost is being paid on every query, including the 90% that are single-hop lookups vector RAG handles at 879 tokens. Route by question type instead.

### 14. LLM-written edges and community summaries at ingestion

The expensive half of every graph pipeline. Extraction-free construction reaches comparable graph quality at **1,043× fewer indexing tokens** ([ContextRAG](https://arxiv.org/pdf/2605.19735)); LazyGraphRAG matches graph answer quality at **0.1% of the index cost**. If a join can produce the edge, an LLM shouldn't be writing it.

### 15. Assuming you have a cache

Authentication silently decides it. Gemini CLI gets context caching on API-key or Vertex auth and **none at all on OAuth**, because Code Assist can't create cached content. Same model, same prefix, same code — 10× the price. Check the provider's auth path before budgeting a single cached token.

### 16. Long TTLs on caches nobody re-reads

Gemini explicit caching bills storage **per hour per million tokens**. A generous TTL on a corpus that went stale is not a safety margin; it's a recurring bill for content you stopped reading. Re-read frequency, not caution, should set the TTL.

### 17. Enabling deletion without watching the hit rate

The reported wins are real (+29% performance, −84% tokens) and the reported cost is real (cache invalidation on every clear). Which one dominates *your* workload is unknowable without a hit-rate metric — see [Law 7](README.md#laws).

### 18. A deletion pass that doesn't persist its own state

[`ClearToolUsesEdit`](https://github.com/langchain-ai/langchain/issues/37815) re-fires every turn against a checkpointer, re-clearing already-cleared results and paying for a fresh token count each time. Deletion bugs cost money in the direction people forget to check.

### 19. A generative LLM for a bounded decision

Routing a ticket, scoring urgency, gating a tool call, or picking one of twenty labels does not need a text stream — it needs a `choice`, a `score`, or a `noul`. A generative model is asked to *write* the answer and then have it parsed, which adds output tokens, latency, a schema validation step, and a hallucination surface where none was required. [Jev's independent benchmark](https://arxiv.org/abs/2609.37647) ran **346,009 classification requests for under US$10**; the same work against a frontier LLM is a different order of magnitude. This is the largest single reduction on the Output leg and it is a *model* choice, not a prompt. ⚠️ The exception is load-bearing: anything needing explanation, multi-step reasoning, or an unbounded answer still needs the LLM.

---

## See also

- [Awesome Token Minimalism](README.md) — the list proper
- [Open problems](OPEN-PROBLEMS.md) — what nobody has measured yet
- [Token ledger](README.md#token-ledger) — advertised vs. independently measured
- [Token Maxxing](TOKENMAXXING.md) — the negative-result catalog, where these defaults appear as graded cases
- [Evidence grades](README.md#evidence-grades) — the one non-negotiable rule

