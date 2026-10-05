# Awesome Token Minimalism

> **Minimal in, minimal out, minimal forever.**
> Papers, tools, and patterns for spending fewer tokens on all three sides of an LLM call.

A token is spent **once when you send it**, **once when you receive it**, and
**every day after** for everything you emitted. Most of the industry optimizes
the first. The bill for the third is the one nobody has instrumented.

---

## What you actually save

Token minimalism is not an aesthetic. Reducing tokens buys three things at once,
and they are the three things every engineering budget is made of.

| Gain | The number |
|---|---|
| 💰 **Money** | Cache reads are **0.1×** input price — a 90% discount. Output is **~5×** input. Reasoning tokens are **>80% of total output cost** on some workloads and usually invisible on the dashboard. Context editing measured **−84% tokens** on a 100-turn eval. Graph indexing done the expensive way is ~**1,000×** the cost of the cheap way. |
| ⏱️ **Time** | Caching: **13–31%** faster first token. Precomputed KV (CAG): **0.85s vs 9.25s** on HotpotQA — ~11×, up to ~17×. Chain of Draft: **4.2s → 1.0s** per answer. Code-execution harnesses report **~79% faster** on multi-step work. And the failure case nobody prices: agents that exhaust context start *retrying*, and **6 of 13 tool calls** hit context overflow in one measured trace. |
| 🔋 **Energy** | Response-length control alone is **25–60% energy reduction** with quality preserved — the core answer turns out to be only **42%** of a typical response. Frontier inference is a median of **0.31 Wh/query**; a *reasoning* query at ~5,000 output tokens is **~13×** that. DeepSeek-R1 measured **20.9 Wh/query against 0.21 Wh** for a conventional model — ~100×. A short session can draw ~**0.5 litres of cooling water**. |

### Why one lever moves all three

The mechanism is an asymmetry in how transformers work:

- **Input tokens are processed in parallel** and their key/value state can be
  cached and reused. Cheap in wall-clock, cheap in energy, and *deeply*
  discountable in price.
- **Output tokens are generated sequentially.** One at a time. Unavoidably.
  Which is why **energy per query tracks output length and not task
  complexity** — and why output costs 5× and reasoning costs 13×.

So tokens are the upstream quantity. Cut them and all three gains follow. That
is the whole bet: the same change that lowers the bill also lowers the latency
*and* the kilowatt-hours, because all three are billed per token.

### And the honest part

The three gains usually move together, but not always, and the exceptions are
worth knowing:

- **Speculative decoding** cuts latency 2–3× and cost ~60% while reducing
  **zero tokens**. It's a serve-side win — filed separately, not claimed here.
- **Precomputing a KV cache** buys query speed with **permanent resident
  memory** (18GB vs 12GB in the CAG benchmark). Time is bought, not created.
- **A stale cache with a long TTL** costs money and energy for content nobody
  reads.
- **Aggressive compression** can save tokens *and cost more*, once you count the
  cache you invalidated and the re-fetching you caused — see
  [Break-even](#%F0%9F%A7%AE-break-even).

None of that weakens the case. It means the case has to be measured rather than
asserted, which is the entire point of the grades below. **Every number in the
table above is graded at its own entry** — the summary is a signpost, not a
citation.

### The scale it adds up to

- Data centres used **448 TWh** in 2025 — more than all but ten countries — and
  **AI is ~20% of that, projected to 40% by 2030**.
- Inference can be up to **90% of a model's total lifecycle energy**. Training
  is the headline; inference is the bill.
- Response length is the most direct lever anyone outside a datacentre has, and
  the one that requires no new hardware, no new model, and no new code.

> **Money is the argument that gets a budget approved. Time is the argument that
> gets a developer to adopt it. Energy is the argument that makes it worth
> doing.** All three move for the same reason, which is why this list only
> tracks one quantity.

---

## Contents

- [What you actually save](#what-you-actually-save) — money, time, and energy, from one lever
- [How to read this](#how-to-read-this)
- [Glossary](GLOSSARY.md) — every load-bearing term, defined once
- [The three legs](#the-three-legs) — the frame everything else hangs on- [What counts as bloat](#what-counts-as-bloat) — and why the enemy is never capability
- [Evidence grades](#evidence-grades) — the one non-negotiable rule
- [Leg 0 — Measure](#leg-0--measure) — you cannot cut what you cannot see
- [Leg 1 — Input](#leg-1--input) — what you send
  - [📏 Effective context](#%F0%9F%93%8F-effective-context) — why every section after it exists
  - [🕸️ Graph engineering](#%F0%9F%95%B8%EF%B8%8F-graph-engineering) — 879 tokens vs 331,375 on the same corpus
  - [🖼️ Multimodal tokens](#%F0%9F%96%BC%EF%B8%8F-multimodal-tokens) — same pixels, ~16× spread
  - [🗑️ Delete](#%F0%9F%97%91%EF%B8%8F-delete) — and why it spends your cache
  - [💾 Cache](#%F0%9F%92%BE-cache) — three mechanisms people conflate
- [Leg 2 — Output](#leg-2--output) — what you get billed for
- [Leg 3 — Lifetime](#leg-3--lifetime) — what you emit becomes context forever
- [Serve-side](#serve-side-cost-and-latency-not-token-count) — cheaper without being fewer
- [Interaction matrix](#interaction-matrix) — where this list argues with itself
- [🧮 Break-even](#%F0%9F%A7%AE-break-even) — the arithmetic that settles those arguments
- [Laws](#laws)
- [Token ledger](#token-ledger) — advertised vs. measured
- [Open problems](#open-problems) — nobody has measured these
- [Anti-patterns](#anti-patterns) — defaults that shipped unmeasured
- [Contributing](#contributing)

---

## How to read this

This list is long because the topic has three independent failure modes and
almost every tool addresses exactly one of them. Four routes, depending on why
you're here:

| If you want to… | Read |
|---|---|
| **Argue with the premise** | [The three legs](#the-three-legs) → [What counts as bloat](#what-counts-as-bloat) → [Interaction matrix](#interaction-matrix) |
| **Cut a bill this week** | [Leg 0](#leg-0--measure) (see the waste) → [Leg 1 · Budget](#%F0%9F%93%90-budget) and [Leg 2 · Audit](#%F0%9F%93%90-audit) (find the two invisible costs) → [Token ledger](#token-ledger) (don't trust the tool's homepage) |
| **Build an agent** | [Effective context](#%F0%9F%93%8F-effective-context) → [Select](#%F0%9F%94%8E-select) → [Isolate](#%F0%9F%A7%B1-isolate) → [Reason less](#%F0%9F%A7%A0-reason-less) → [Laws](#laws) |
| **Justify it upward** | [What you actually save](#what-you-actually-save) (money, time, energy) → [🧮 Break-even](#%F0%9F%A7%AE-break-even) (the arithmetic) → [Token ledger](#token-ledger) (the cautionary half) |
| **Review a tool someone recommended** | [Evidence grades](#evidence-grades) → [Token ledger](#token-ledger) → [Anti-patterns](#anti-patterns) |

Two conventions worth knowing before you start:

- **Every entry carries an evidence grade.** `[measured]` means someone stated a
  baseline and a method. **None of the four popular tools with independently
  audited numbers hit their headline** — one was *more expensive* than doing
  nothing. See [Token ledger](#token-ledger). The grade is the list, not the
  commentary.
- **The enemy is bloat, never capability.** Every entry keeps the feature and
  removes an unmeasured cost. If a technique can't be written that way, it's in
  [Anti-patterns](#anti-patterns) instead.

---

## The three legs

| | Leg | Clock | Multiplier | Failure mode | Levers |
|---|---|---|---|---|---|
| ◀️ | **Input** — what you send | this call | 1× | context rot | retrieval, compression, caching, deletion |
| ▶️ | **Output** — what you're billed for | this call | **~5×** | overthinking, verbosity | budgets, format, reasoning length, edit protocol |
| ⌛ | **Lifetime** — what you emit becomes context | **every future call** | compounding | artifact bloat | build less, prune what you emitted, retention bars |

Output is 5–25× the price of input on current frontier pricing. Lifetime is the
leg with no tooling, no dashboards, and no agreed vocabulary.

The three legs run on different clocks, which is why trade-offs between them are
so rarely stated. See [Interaction matrix](#interaction-matrix).

### Input, in one line

Adding context is the field's default setting, and it rests on a premise that no
longer holds. Context is not a bucket — it is a **finite attention budget with
diminishing returns.** Every model tested got measurably worse as input grew,
long before any stated limit. See [Effective context](#%F0%9F%93%8F-effective-context).

### Output, in one line

Most of your output bill is invisible. **Reasoning tokens are billed at the
output rate** and usually aren't broken out on any dashboard. One call with an
8,200-token thinking pass cost **7.2× more** than the same call without it —
with an identical visible response. See [Leg 2](#leg-2--output).

### Lifetime, in one line

Every line an agent generates is a permanent charge on every future session that
touches that subsystem. OpenClaw deleted **~400k LOC of its own tests** with
little change in coverage. See [Leg 3](#leg-3--lifetime).

---

## What counts as bloat

Bloat is only useful as a category if it is falsifiable. So:

> **Bloat is any token in the request, the response, or the artifact whose cost
> has not been measured against its contribution.**

Three consequences:

- **Capability is never bloat.** A 1M-token window holding 40k of high-signal
  context is fine. A 32k window stuffed with 30k of guessed-at relevance is
  bloat. The unit of analysis is the *token*, never the *capability*.
- **Bloat is a default, not a decision.** Nobody chose to load 91 tool schemas
  on connect. Nobody chose 8,200 thinking tokens on every call. Bloat is what
  ships when a default goes unmeasured — which makes it a bug, and bugs are
  fixable.
- **The exit from bloat is a receipt.** Not taste. A number.

**Capability that hasn't been measured is not bloat.** Every entry here passes
that bar: the capability is preserved, and the number moves. In almost every
well-measured case, quality went **up** at the same time — deleting bloat frees
attention, which is the same mechanism as context rot.

### A useful asymmetry

The **same mechanism** produces bloat in three different places:

> A README claiming −65% that delivers −8.5% is the same artifact as 91 tool
> schemas injected on every turn: something shipped as a default benefit,
> unmeasured, with the cost landing on the bill.

That is why the [token ledger](#token-ledger) is part of this list, not an
appendix to it.

---

## Evidence grades

Every entry carries one. It is the only editorial rule here that is not negotiable.

| Grade | Means |
|---|---|
| `[measured]` | a number with a stated baseline and method someone could re-run |
| `[self-reported]` | a number from the tool's own authors, baseline or harness unstated |
| `[asserted]` | a claim with no number — the default for anything marketing-shaped |
| `[negative]` | measured, and it did **not** work |

`[negative]` and `[asserted]` are not padding. They are the credibility
mechanism, and they are the reason this list is worth reading: most token-savings
marketing is `[asserted]`, and **none of the four popular tools that have been
independently audited hit their claimed number** — one made the bill go *up*.
See the [ledger](#token-ledger).

Where a result is model-, harness-, or date-specific, say so inline. These
tools move weekly; an unstamped number is worthless within a month.

---

## Leg 0 — Measure

You cannot cut what you cannot see. Most teams have totals and no composition,
which is why they cannot attribute cost or find the biggest lever.

- **[contextlens-profiler](https://pypi.org/project/contextlens-profiler/)** — `py-spy` for your prompt. Decomposes the window by region, shows re-billing across turns, names waste patterns (`stale tool result`, `unused tool schema`) with a dollar cost and a one-line fix each. `[measured]`
- **[contextwatch](https://pypi.org/project/contextwatch/)** — per-turn token ledger; detects *server-side* compaction (`clear_tool_uses`, `compact`) that client-side hash diffing cannot see, because those never touch your messages list. Replay-probes pre/post compaction to score how much recall the compaction destroyed. `[self-reported]`
- **[contextspy](https://github.com/RimantasZ/contextspy)** — wraps codex/copilot/opencode; splits input into 8 categories and diffs context between turns. `[self-reported]`
- **[ContextScope](https://github.com/ashutosh160798/context-scope)** — local-first macOS debugger; drop-in OpenAI-compatible proxy on `:4319`, animated token-pressure view, timeline replay, warnings at 70/85/95%. `[self-reported]`
- **[ctxlens](https://github.com/dabit3/ctxlens)** — CLI. `ctxlens --mcp ./server` to price a server's schemas before you connect it. `[self-reported]`
- **[ctxbudget](https://github.com/davidcjw/ctxbudget)** — audits everything your agent auto-loads: `CLAUDE.md`, `AGENTS.md`, `.cursor/rules`, `copilot-instructions.md`, plus recursive `@import`. Measures duplication *across* files. `--fail-under` for CI. `[self-reported]`
- **[skill-context-doctor](https://github.com/aptratcn/skill-context-doctor)** — bloat diagnosis across skills, MCP servers, and memory files; flags hoarding patterns. `[self-reported]`
- **[ccusage](https://github.com/ccusage/ccusage)** — cost across 16 agent CLIs from local session data. Bills, not estimates. `[measured]`
- **[Claude Code `/context` breakdown](https://github.com/Beaulewis1977/claude-code-context-command)** — reference numbers for what a session costs *before you type*: system prompt ~8.5k, built-in tools ~15.2k, MCP schemas variable (one real setup: 135.6k, 76.6% of the window). `[self-reported]`

> **A tool's own savings counter is not evidence; only the bill is.**
> `rtk`'s built-in analytics reported *96.2M tokens saved, 99.8% of everything
> it touched* — while the measured bill for the same trials went **up**.

---

## Leg 1 — Input

What you send. Ordered by how much it removes, cheapest first: the evidence
that it should be less, then budget it, fetch less, structure it, shrink it,
hide it from the model, delete it, and finally stop re-sending it.

### 📏 Effective context

The measurement that justifies every Input section below. Short prompts are not
just cheaper — they are *better*, and this is the evidence.

- **[Context rot (Chroma, 2025)](https://research.trychroma.com/context-rot)** · `18 models, all degraded` · `[measured]`
  Across 18 frontier models including GPT-4.1, Claude 4, Gemini 2.5, and Qwen3: performance degrades as input length grows, well before any stated limit, and **distractors have non-uniform impact** — some waste far more attention than others. The LongMemEval arm is the cleanest version of the argument: **focused input (only relevant parts) versus full input (all 113k tokens, same question)** — focused wins across every model tested. Replication toolkit: [chroma-core/context-rot](https://github.com/chroma-core/context-rot).
- **[RULER (NVIDIA)](https://github.com/NVIDIA/RULER)** · `claimed 128K, effective 64K` · `[measured]`
  13 tasks across 4 categories, 4K→128K, with an explicit **effective context length** threshold. Models that score near-perfect on needle-in-a-haystack degrade sharply on multi-hop tracing and aggregation. GPT-4-1106 claims 128K and effectively manages 64K; Llama3.1-70B falls off a cliff after 64K. Near-perfect NIAH is not evidence of usable context.
- **[Lost in the Middle (TACL 2024)](https://aclanthology.org/2024.tacl-1.9/)** · `mid-context info → closed-book accuracy` · `[measured]`
  Performance peaks when the relevant span sits at the beginning or end of the context and falls to roughly closed-book accuracy when it sits in the middle — **including in models explicitly trained for long context.** The practical consequence: position is a lever, and a document you could have sliced into two targeted queries does not have to be paid for in full.

> **Read these three together and the Input leg follows.** Effective context is
> shorter than advertised, degrades before the wall, and is non-uniform in
> *which* tokens you add. That is why the sections below are ordered by how
> much they remove, not by how clever they are.

### 📐 Budget

Allocate the window before you fill it. A cap set uniformly across heterogeneous
work is itself bloat.

- **[Anthropic: advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)** — explicit decision thresholds. Use Programmatic Tool Calling when tool definitions exceed 10k tokens, when tool-selection accuracy is a problem, or with 10+ tools. *Don't* when the library is under 10 tools, all are used every session, and schemas are compact. `[measured]`
- **[ctxbudget CI gate](https://github.com/davidcjw/ctxbudget)** — `--fail-under 80` fails a build when context health drops. `[self-reported]`
- **[CLAUDE.md ≤ 3k tokens](https://github.com/JoeArmageddon/Claude-Master-Skill/blob/main/docs/token-budget.md)** — the 3,000-token / 40-instruction cap, and the finding behind it: adherence degrades past ~150–200 total instructions, *including the ones you care about*. Also: MCP server limit of 10. `[self-reported]`
- **[< 100 lines of CLAUDE.md](https://gist.github.com/yurukusa/556f67c493a2729ce9b1703f5003a227)** — 50–100 lines is the balance; 200+ means split into `.claude/rules/`. Plus allowlist-over-blocklist and move-safety-rules-to-hooks. `[self-reported]`
- **[TALE (ACL 2025)](https://aclanthology.org/2025.findings-acl.1274/)** — noted here only because the *technique* generalises: have the model **estimate its own budget before it spends it.** TALE applies it to reasoning tokens and gets −67%; the same estimate-then-constrain shape works for context. Its numbers live in [Leg 2 · Budget](#%F0%9F%8E%AF-budget). `[measured]`

### 🔎 Select

Retrieval is a **runtime** decision, not a preprocessing step. Hold identifiers
(a file path, a query, a URL) and load the payload when the task needs it.

- **[Anthropic: effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — the canonical statement: *find the smallest possible set of high-signal tokens*. Attention budget, n² pairwise relationships, just-in-time retrieval, progressive disclosure, compaction, note-taking, subagents. (Tool-result clearing from the same post has its own section: [Delete](#%F0%9F%97%91%EF%B8%8F-delete).) `[measured]`
- **[Tool Search Tool](https://www.anthropic.com/engineering/advanced-tool-use)** — 134k → 8.7k tokens, **and** tool selection improved: Opus 4 49% → 74%, Opus 4.5 79.5% → 88.1%. Fewer schemas, better choices. `[self-reported]`
- **[MCP client best practices](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/docs/2026-07-28/develop/clients/client-best-practices.mdx)** — progressive discovery + programmatic tool calling, with the threshold at which to switch. `[measured]`
- **[RAG-MCP](https://arxiv.org/html/2505.03275v1)** — semantic retrieval over MCP schemas; retrieve top-k tool descriptions instead of all of them. `[measured]`
- **[SEP-1576: mitigating token bloat in MCP](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576)** — schema redundancy analysis, URL-addressed schemas, embedding-based tool retrieval. `[measured]`
- **[python-sdk #2619: context bloat is the MCP bottleneck](https://github.com/modelcontextprotocol/python-sdk/issues/2619)** — the structural case for grouping: no partial-loading primitive in the spec, so every workaround lives above the protocol. `[measured]`
- **[Serena](https://github.com/oraios/serena)** — symbol-level retrieval and editing over LSP. Ships `.serena/memories/` for cross-session orientation. ⚠️ See the negative result below. `[asserted]`
- **[serena-slim](https://github.com/mcpslim/serena-slim)** — 29 tools → 18, schema tokens 7,348 → 1,614 (−78%). Good example of tool consolidation as a token lever. `[self-reported]`
- **[SWE-grep (Cognition)](https://cognition.com/blog)** — RL-trained agentic retrieval for fast parallel context fetch, order of magnitude less time than frontier coding models. `[self-reported]`

### 🕸️ Graph engineering

A graph is a **token-efficiency choice**, not just a retrieval architecture. It
can be the cheapest way to answer a question (structured facts beat 4k tokens of
nearby prose) or by far the most expensive (community summarization inflates
prompts 5–6 orders of magnitude). Both are real and both are measured.

Average prompt tokens per query, same corpora:

| System | Novel | Medical |
|---|---|---|
| Vector RAG | **879** | **954** |
| RAPTOR | 3,441 | 3,510 |
| fast-graphrag | 4,204 | 4,298 |
| HippoRAG | 7,208 | 7,342 |
| LightRAG | 100,832 | 100,310 |
| MS-GraphRAG local | 38,707 | 39,821 |
| MS-GraphRAG global | **331,375** | **332,881** |

Two vectors beat every graph on the token column while losing on *context
relevance* — graphs reach more relevant information and pay in redundancy.
Global community summarization scales **with corpus size**: 7,800 → 40,000
tokens as query difficulty rises. That is the worst token curve in this list.

**The split that matters:** *which* graph system. Same paper, same corpus, 377×
between the cheapest and dearest.

- **[When to use Graphs in RAG (2025)](https://arxiv.org/html/2506.05690v3)** — the table above, plus the finding that graph pipelines "incur non-trivial token overhead" while introducing redundancy that degrades context relevance. Vector RAG wins Evidence Recall on discrete-fact questions (83.2%); GraphRAG-global wins it on multi-hop (83.1%) but loses Context Relevance (78.8% vs RAG's). `[measured]`
- **[GraphRAG vs RAG: systematic evaluation](https://www.alphaxiv.org/abs/2502.11371)** — construction cost is "significantly more time-consuming and expensive" than vector indexing, but community-based GraphRAG can achieve *lower query latency* because summaries collapse the search space. Also the storage warning: community systems carry the largest footprint, since they keep both graph structure and every level's summaries. `[measured]`
- **[Relation-grouped graph representation](https://arxiv.org/html/2606.25656)** — the trick worth stealing regardless of framework: collapse `entity1 -r1-> entity2`, `entity1 -r2-> entity2` into `entity1 -(r1|r2|r3)-> entity2`, taking per-entity token cost from **O(n) to O(1)** in relation count. Same knowledge, compact serialization. `[measured]`
- **[LazyGraphRAG (Microsoft Research)](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost)** — defers LLM use entirely: **indexing cost identical to vector RAG and 0.1% of full GraphRAG**, matching or beating answer quality at query budgets up to 1,500 relevance tests. The existence proof that graph quality does not require the expensive index. `[measured]`
- **[Dynamic community selection (MSR)](https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection)** — the in-query fix for global search: rate communities for relevance, then traverse only the useful ones. **−77% tokens** at community level 1 (1,500 reports → 470) with comparable quality. ⚠️ At level 3 it costs **+34%** — the rating pass pulls in deeper reports. Match the technique to the level. `[measured]`
- **[TERAG](https://arxiv.org/html/2509.18667v3)** — token-efficient graph construction by dropping LLM-written edges: **−89…97% output tokens** vs other graph-RAG methods, matching GraphRAG-level accuracy on 2Wiki (EM 51.2 vs 51.4) at a fraction of the tokens. `[measured]`
- **[ContextRAG](https://arxiv.org/pdf/2605.19735)** — extraction-free construction via soft fuzzy join / meet operations instead of LLM-written edges. Indexes with **30 LLM calls and 22,073 tokens**; a HiRAG reproduction needed 870 calls / 3.54M tokens on a 20-task subset and failed mid-construction. **1,043× fewer indexing tokens, 188× fewer calls.** The clearest demonstration that graph structure ≠ LLM summarization. `[measured]`
- **[RAG vs GraphRAG win rates](https://medium.com/@pankaj_pandey/microsoft-graphrag-a-breakthrough-for-global-questions-a-downgrade-for-everything-else-22b294bb3292)** — GraphRAG global is a real win on dataset-wide questions and a downgrade for everything else. `[asserted]`

**Agent memory is the same trade with a different clock.** The failure mode
shifts from query-time prompt size to *ingestion-time* cost and staleness:

- **[Graph-based agent memory survey (2026)](https://arxiv.org/pdf/2602.05665v1)** — taxonomy across KG / hierarchical / temporal / hypergraph / hybrid, with the selection rule: precision and explicit multi-hop favor relational graphs; compression and abstraction favor hierarchical summaries; temporal fidelity motivates temporal graphs; cross-modal fuzzy recall favors vector or hybrid. `[measured]`
- **[True Memory — "Storage Is Not Memory"](https://arxiv.org/html/2605.04897v1)** — the sharpest negative in this section, and it indicts the whole family. Extraction at ingestion is the wrong primitive: **content discarded before the query is known cannot be recovered at retrieval time.** Argues the extraction family (Mem0, Zep, Graphiti, Supermemory, EverMemOS) inverts the relationship — it commits content to a fixed schema at ingestion and "the representation becomes the memory." Their counter: single SQLite file, no graph store or vector index, 87.8% on LongMemEval (n=500). `[measured]`
- **[Zep / Graphiti](https://help.getzep.com/)** — temporal Context Graph with bitemporal fact validity, so "no medication in January" and "new prescription in March" stay distinct rather than one overwriting the other. `[self-reported]`
- **[Neo4j agent memory architecture](https://neo4j.com/labs/agent-memory/explanation/graph-architecture)** — the graph-native case: index-free adjacency gives O(1) direct lookups and O(k) 2-hop traversal where relational is O(n·log n). `[asserted]`

#### Graphs with no LLM in the loop

Every large number in the table above comes from LLM-written edges or community
summaries. These three build real graphs **without an LLM in the extraction
path** — and one of them does it at 2 billion edges. That makes the section's
central question settled rather than open, at least for these domains.

- **[GitLab Orbit](https://gitlab.com/gitlab-org/orbit/knowledge-graph)** — the strongest existence proof here. Change-data-capture into ClickHouse plus code parsed through an internal API across 11–12 languages; **500 million nodes and 2 billion edges over 40,000+ projects indexed in under 45 minutes**, event-driven so it stays current as changes ship. No LLM writes a single edge. Served to agents over MCP (Claude Code, Codex, Cursor, opencode, Gemini CLI), a Cypher-like DSL, REST, and `glab`. Agents call `get_graph_schema` / `query_graph` only when a question is better answered by traversal, and fall back otherwise. `[measured]/[asserted]` — index build is vendor-reported and checkable; the *cost* claim is asserted, because there is no published token-per-query figure.
  **[Orbit Local](https://github.com/gitlabhq/orbit-knowledge-graph)** is the more interesting shape for this list: a **single binary** that builds a code-only call graph into **one DuckDB file**, offline, no GitLab account required. Multi-repo graphs share one database at `~/.orbit/graph.duckdb`, scoped per repository and branch.
  ⚠️ Beta; the query DSL and ontology may change, and the hosted graph is behind a `knowledge_graph` flag. Worth noting as precedent: Duo queries against Orbit are **zero-rated and don't consume GitLab Credits**.
- **[Logseq](https://logseq.com/)** — local-first markdown/EDN, block-level references, and an **official MCP server** (HTTP or CLI, Streamable transport) that reads and mutates the graph in place. The design detail worth stealing is operational: **batch creates and edits in one invocation** (which per the [ACL 2026 finding](#interaction-matrix) is the cost that actually matters in an agent loop), and a **`pretend` option** — "pretend add page X with y blocks" — so the agent can see how many changes a mutation causes *before* committing it. Every change stays undo/redo-able in-app. `[asserted]`
- **[Obsidian](https://obsidian.com/)** — the graph is derived from `[[wikilinks]]`, so it is **already text on disk**: greppable, git-diffable, and free to index. No embedding step, no extraction step, nothing to pay for. `[asserted]`
- **[obra/knowledge-graph](https://github.com/obra/knowledge-graph)** — makes that explicit and exposes it to agents: parses a vault into an untyped graph (files = nodes, wikilinks = edges) into SQLite with `sqlite-vec` + FTS5, 22MB local embedding model, 10 operations over CLI and MCP. Ships with a Claude Code plugin. Its stated design principle is this list's thesis verbatim: **"No LLM inside the tool — the agent does the reasoning, the tool provides the data infrastructure."** `[self-reported]`
- **[obsidian-graph-mcp](https://github.com/tscolari/obsidian-graph-mcp)** — the purest form, and it answers [True Memory](#%F0%9F%95%B8%EF%B8%8F-graph-engineering) directly: *"your hand-curated links are the graph — no entity extraction, no ontology, no embeddings required."* Unresolved links keep `dst_id NULL`, so **dangling links stay queryable**. That is exactly the recoverability case True Memory argued LLM-extracted graphs lose: nothing is extracted, so nothing can be discarded at ingestion, and a knowledge gap remains addressable later. Frontmatter properties containing wikilinks become typed edges. `[self-reported]`
- **[logseq-graph-mcp](https://github.com/johnschieferleuhlenbrock/logseq-graph-mcp)** — local-only stdio variant, stdlib-only with no external dependencies; cache and diagnostics kept outside the graph directory, file watchers invalidate state after external edits. The careful-deployment-hygiene counterpart to the graph itself. `[self-reported]`

> ⚠️ **Cost of these graphs is not zero — it's tool schemas.** Each MCP server
> here adds 10+ tools to every turn, which is [anti-pattern #1](#anti-patterns)
> wearing a useful hat. Load them through [progressive
> discovery](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/docs/2026-07-28/develop/clients/client-best-practices.mdx)
> or a [tool search](https://www.anthropic.com/engineering/advanced-tool-use)
> layer, or subsume them behind one search-and-traverse tool. A graph that
> answers "what connects to this?" in one call beats ten narrow tools.

> **The rule this section reduces to: never pay an LLM to summarize your index
> when a join would do.** Every large number in the table above traces back to
> LLM-written edges or community summaries at ingestion. Both can be replaced
> with deterministic structure — LazyGraphRAG and ContextRAG do it
> algorithmically, GitLab Orbit does it with change-data-capture, and a
> wikilink vault does it by hand. All four keep the graph.

### 🖼️ Multimodal tokens

The same pixels cost different amounts depending on who tokenizes them, and the
spread is not small. A 1024×1024 image:

| Provider | Formula | Cost |
|---|---|---|
| Gemini | 258 flat if both dims ≤384px; else 258 per 768×768 tile | **258** |
| GPT-4o / 4.1, `detail: low` | flat | **85** |
| GPT-4o / 4.1, `detail: high` | `85 + 170 × tiles`, after fit-to-2048 then shortest-side ≤768 | **765** |
| Claude (standard tier) | `⌈w/28⌉ × ⌈h/28⌉`, downsized to ≤1568px and ≤1568 tokens | **~1,400** |
| Claude (high-resolution tier) | same formula, ≤2576px and ≤4784 tokens | **~1,400** (up to 4,784) |

**Same image, ~16× spread.** And none of it scales with file size — only
dimensions. A 5MB PNG and a 50KB JPEG of the same resolution cost the same, which
means "compress the image" is the wrong instinct and "resize the image" is the
right one.

- **[Anthropic vision: resolution and token cost](https://platform.claude.com/docs/en/build-with-claude/vision)** — one visual token per 28×28-pixel patch. Standard tier caps at 1568px long edge / 1568 tokens; [high-resolution tier](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates) (Claude 4.7+) allows 2576px / 4784. Caps are applied *before* you're billed, so **pre-resizing costs you nothing and saves the upload** — a 1920×1080 screenshot is downsized to 1456×819 regardless. `[measured]`
- **[OpenAI image input cost](https://developers.openai.com/api/docs/guides/image-cost-calculator)** — tile model: `base + tile_tokens × ⌈w/512⌉ × ⌈h/512⌉` after fitting 2048² and clamping the shortest side to 768. Per-model constants: GPT-5/5.1 are 70 + 140, GPT-4o/4.1 are 85 + 170, and **`gpt-4o-mini` is 2,833 + 5,667** — 33× the tile cost of its sibling for the same image. `[measured]`
- **[`detail: low`](https://platform.openai.com/docs/guides/images-vision)** — flat 85 tokens regardless of size. For "is this a chart or a photo", full resolution is a **30× overpay**: 2,805 tokens vs 85 on a large image. `[measured]`
- **[Gemini image tokenization](https://ai.google.dev/gemini-api/docs/tokens)** — 258 flat when both dimensions are ≤384px, otherwise 258 per 768×768 tile. So the cheapest image you can send is 258 tokens, and the lever is *shrinking below 384px*, not compressing. Gemini 3 adds `media_resolution` (LOW 280 / MEDIUM 560 / HIGH 1120 / ULTRA_HIGH 2240) instead of tiles. `[measured]`
- **[Gemini video and audio rates](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/embeddings/get-multimodal-embeddings)** — video at 263 tokens/second, audio at 32/second, 66 per sampled frame. **A one-minute video is ~15,780 tokens** — a full context window, for one clip, before any question is asked. Sample frames on purpose. `[measured]`
- **[Browser automation: snapshot vs screenshot](https://github.com/JuliusBrussee/caveman)** — a focused question against a 200-row table: **121 tokens as a Playwright ARIA snapshot versus 15,704 as a screenshot — 129.8×** cheaper, and the tree gives exact element handles instead of pixel coordinates. The honest caveat from the same benchmark: on tiny forms the snapshot *loses*, 2.3×, because the tree carries structural overhead the image doesn't. `[self-reported]`

**Rules**

1. **Pass a reference, not bytes.** File paths, URLs, or a Files-API handle. The
   model fetches what it needs; you don't pay to move pixels through the context
   twice.
2. **Prefer a structured representation to a rendering.** Accessibility tree over
   screenshot, extracted table over page image, transcript over audio waveform.
   Same information, 1–2 orders of magnitude fewer tokens, usually more precise.
3. **Resize to the provider's cap.** Every provider downsizes before billing, so
   sending more resolution is buying nothing. Pre-resizing also cuts TTFT.
4. **Land on tile boundaries.** OpenAI tiles at 512px: a 770px image is **4
   tiles / 765 tokens**, while 512px is **1 tile / 255 tokens** for a 3× saving.
   Pure arithmetic, no quality loss.
5. **`detail: low` when you only need to know what it is.** Full resolution is for
   reading text and fine detail, not for classification.
6. **Don't put the same image in twice.** A screenshot in the user turn and again
   in a tool result is two full charges; reference it.

> **The framing that transfers:** an image is a *serialization format*, and so is
> the accessibility tree, and so is an extracted table. Pick the serialization
> with the lowest token cost that still carries the decision-relevant
> information. That is the same judgment as [Graph engineering](#%F0%9F%95%B8%EF%B8%8F-graph-engineering)
> and [Select](#%F0%9F%94%8E-select), applied to pixels.

### ✂️ Compress

Loss-aware compression of what you send.

- **[LLMLingua (EMNLP 2023)](https://aclanthology.org/2023.emnlp-main.825/)** · `up to 20×, EM preserved; response length −20…30%` · `[measured]`
- **[LongLLMLingua](https://arxiv.org/html/2310.06839v2)** — long-context variant; question-aware compression, document reordering, subsequence recovery so entities don't get mangled. `[measured]`
- **LLMLingua-2, Selective Context, 500xCompressor, RECOMP, xRAG, CompAct, QGC** — see the [compression survey (NAACL 2025)](https://aclanthology.org/2025.naacl-long.368/) for the taxonomy and the honest failure modes. `[measured]`
- **[headroom](https://github.com/headroomlabs-ai/headroom)** — local-only compression layer (library / proxy / agent-wrap). 55,957 → 24,340 tokens; sub-millisecond. Reports GSM8K ±0.000 and TruthfulQA +0.030. Notably recommends *also* pairing with Serena and Ponytail — cross-layer by design. `[self-reported]`
- **[Context compression skill (muratcankoylan)](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-compression/SKILL.md)** — two contributions worth more than the tooling: **optimize tokens-per-*task*, not tokens-per-request** (compression that loses a file path causes re-fetching that costs more than it saved), and **never compress tool definitions or schemas**. `[asserted]`

> ⚠️ **Compression and caching are antagonistic.** Compressing rewrites the
> prefix, so every call becomes a cache miss. Naive compression can be *net
> negative*. See [CAPC](https://arxiv.org/html/2607.15516v1) — cache-aware
> compression, −51.7% on a 94k tool-schema prefix. And a clean reason it happens
> is in the survey: soft-prompt methods encode context into special tokens the
> base model was never tuned for.

### 🧱 Isolate

Keep intermediate data out of the model. The model should see conclusions, not
pipes.

- **[Anthropic: code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)** · `150k → 2k tokens (−98.7%)` · `[measured]`
  Tools become files on a filesystem; the model reads them on demand. Loops, conditionals, and error handling run in code instead of alternating tool call / sleep. Intermediate results never enter the window.
- **[Programmatic Tool Calling](https://www.anthropic.com/engineering/advanced-tool-use)** · `43,588 → 27,297 avg (−37%)` · `[measured]`
- **[Cloudflare: Code Mode](https://blog.cloudflare.com/code-mode/)** — the same convergence from the other direction. `[measured]`
- **[mcp-server-code-execution-mode](https://github.com/elusznik/mcp-server-code-execution-mode)** — rootless discovery-first bridge: ~30k → ~200 tokens, constant overhead. `[self-reported]`
- **[mcp-compressor (Atlassian)](https://www.atlassian.com/blog/developer/mcp-compression-preventing-tool-bloat-in-ai-agents)** — proxy that compresses tool descriptions 70–97%, expanding schemas only on demand. `[self-reported]`
- **[Cognition: Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)** — and the honest follow-up, [Multi-Agents: What's Actually Working](https://cognition.com/blog/multi-agents-working). Read both. The first says share full traces, not messages; the second says the shape that works is map-reduce-and-manage, and that agents should contribute intelligence while **writes stay single-threaded**. `[measured]`

### 🗑️ Delete

Stop paying for context you have already consumed. Two implementations, one
tradeoff: you can delete it yourself, or let the provider delete it for you —
and the second one quietly spends your cache.

#### Client-side: you decide what goes

- **[Anthropic: tool result clearing](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — described as the safest, lightest touch: clear the tool result after the turn in which it was consumed, keep the model's own summary of it. `[measured]`
- **[Contextual Memory Virtualisation](https://github.com/CosmoNaught/claude-code-cmv)** — strip tool-result bodies, base64 blocks, and thinking signatures while keeping every user and assistant message verbatim. 132k → 2.3k. Adds named snapshots, branching, and trimming: version control for context. `[self-reported]`
- **[`/clear` vs `/compact`](https://github.com/jaczaar/claude-code-bestpractices/blob/master/research/02-context-management.md)** — `/compact` summarizes and keeps you in the same topic; `/clear` is a hard reset. Don't carry a database migration into a frontend feature. `[asserted]`
- **[contextwatch](https://pypi.org/project/contextwatch/)** — find *which* result is still costing you: the turn-3 tool output still billing 8k tokens at turn 20. (Listed in [Leg 0](#leg-0--measure); repeated here because deletion is what you do with the answer.) `[self-reported]`

> ⚠️ **Deletion has a blast radius.** [microcompact silently cleared MCP-backed
> user memory](https://github.com/anthropics/claude-code/issues/57788) — no
> notice, no opt-in, and the model could not self-diagnose the loss. Deleting
> output that a downstream system treats as durable storage is not an
> optimization. **Verify the summary before you delete the source.** See
> [Leg 3 retention bars](#%F0%9F%AA%9E-retention-bars--dont-delete-without-one).

#### Provider-side: the provider does it for you

Strong numbers — and it spends your cache to get them.

- **[Anthropic: managing context on the Claude Developer Platform](https://claude.com/blog/context-management)** — the measured case: **context editing alone +29%** agentic-search performance over baseline; **memory tool + context editing +39%**; and on a **100-turn web search eval, −84% token consumption** while completing workflows that would otherwise fail on context exhaustion. `[measured]`
- **[Context editing API](https://platform.claude.com/docs/en/build-with-claude/context-editing)** — beta header `context-management-2025-06-27`; strategies `clear_tool_uses_20250919` and `clear_thinking_20251015`. Tunable `trigger` (default 100k input tokens), `keep`, `exclude_tools`, `clear_tool_inputs`. `[measured]`
  ⚠️ **Three documented sharp edges, worth reading before enabling:**
  - *"Tool clearing will invalidate your cache if your prefixes contain your tools."*
  - Thinking blocks: **kept** → cache preserved; **cleared** → cache invalidated at that point. You are choosing between window space and cache hits, explicitly.
  - For accounts created **on or after 2026-08-31**, replaying an invalidated block is **rejected** unless you opt into dropping it.
- **[Anthropic memory tool](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-tool-use.html)** — Claude reads and writes a developer-owned local directory, so durable state lives *outside* the window instead of inside it. The same move as structured note-taking, with the storage backend under your control. `[measured]`
- **[LangChain `ClearToolUsesEdit`](https://reference.langchain.com/python/langchain/agents/middleware/context_editing/ClearToolUsesEdit)** — model-agnostic port, with triggers in tokens, messages, or **fraction of the model's window** (`{fraction: 0.8}`). Note `clear_at_least`: the API ships a knob whose documented purpose is "determining whether context clearing is worth breaking your prompt cache for." The tradeoff is a first-class parameter. `[self-reported]`
- **[langchain #37815](https://github.com/langchain-ai/langchain/issues/37815)** — ⚠️ `ClearToolUsesEdit` **fires every turn** when a checkpointer is present: edits run on a `deepcopy`, so the `cleared` flag never persists back to state. The edit re-applies forever, and `token_count_method="model"` keeps paying for token counts on unchanged state. A deletion feature that silently costs money on every request. `[negative]`
- **[LiteLLM context management polyfill](https://docs.litellm.ai/docs/claude_code_context_management)** — applies `clear_tool_uses` in-gateway for any non-Anthropic provider, so you write the loop once. (`clear_thinking` listed as coming soon.) `[self-reported]`

> **The tradeoff to hold onto:** clearing tool results and keeping them are both
> defensible, and which wins depends on your cache hit rate — not your token
> count. Deletion moves cost from every-turn to once-per-invalidation. If you
> can't see your hit rate, you can't tell whether you're saving or spending,
> which is why [rule 4 of Cache](#%F0%9F%92%BE-cache) is the one to read first.


### 💾 Cache

Cheapest input tokens are the ones you don't re-send.

But "caching" names **three genuinely different mechanisms** on different
clocks, and conflating them is how teams ship a cache that saves nothing:

| Mechanism | What it reuses | Saves | Breaks when |
|---|---|---|---|
| **Prefix caching** | identical prompt prefix, provider-side | input $ + TTFT | anything in the prefix changes |
| **KV precompute / CAG** | computed KV states, offline | prefill compute, TTFT | model or corpus changes |
| **Semantic / response caching** | whole answers by similarity | everything | nothing, but it's a different system |

A fourth thing gets called "caching" and isn't: **provider-side deletion**. It
reuses nothing, it just removes tokens, and it has the awkward property of
**invalidating the prefix you just built.** It's in
[Delete](#%F0%9F%97%91%EF%B8%8F-delete) because that's what it is.
[CAPC](https://arxiv.org/html/2607.15516v1) shows the same collision arriving
from the compression side.

#### 🏷️ Prefix caching (provider-side)

- **[Anthropic: prompt caching](https://claude.com/blog/prompt-caching)** — write costs 1.25× base input, reads cost 0.1×. Up to −90% cost, −85% latency on long prompts. `[measured]`
- **[Don't Break the Cache](https://arxiv.org/html/2601.06007v1)** — across OpenAI/Anthropic/Google: **45–80% cost, 13–31% TTFT**. Cache-safe strategies beat naive full-context caching, and cost savings scale with prefix length (10–45% at 500 tokens → 54–89% at 50,000). Also the part everyone gets wrong: **what invalidates a prefix** — a timestamp or request ID in the system prompt, tool-definition changes, mid-session model switches, toggling thinking parameters. `[measured]`
- **[Gemini context caching](https://ai.google.dev/gemini-api/docs/generate-content/caching)** — implicit (automatic on 2.5+, **no savings guarantee**) vs explicit (**guaranteed** 90% discount, TTL defaults to 1 hour). Minimums vary by model: 2,048 tokens on Gemini 2.5, 4,096 on the Gemini 3 family, 6,144 for some 3.x Flash. Two sharp edges: explicit caching bills **storage per hour per million tokens**, so a cache you never re-read is a pure loss; and the Interactions API supports implicit only. `[measured]`
- **[Vertex AI context caching](https://cloud.google.com/vertex-ai/generative-ai/docs/context-cache/context-cache-overview)** — 90% discount; implicit has **no cache-write surcharge** (tokens written are charged at standard input). Caches deleted within 24h, retention based on load and reuse frequency. `[measured]`
- **[Gemini CLI token caching](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/token-caching.md)** — ⚠️ **caching requires API-key or Vertex auth. OAuth users get none**, because the Code Assist API doesn't support cached-content creation. If your team authenticates with a Google account you have no cache, and nothing in the product tells you. `/stats` shows the split. `[measured]`
- **[Why caching is also an energy lever](https://arxiv.org/abs/2607.26571)** — inference energy decomposes into compute, parameter access, **KV-cache write, and attention read**. A prefix hit skips the KV work entirely, so the joules don't get spent either. Caching is the rare optimization that is unambiguously good on all three axes: cheaper, faster, and lower-energy, with no counter-lever. `[measured]`

**Rules that matter more than the features:**
1. Stable content first (system prompt → tool definitions → history), variable last.
2. Keep the prefix byte-identical between turns. A request ID in the system prompt kills every subsequent hit.
3. Cache operates on ~1k-token blocks. A 300-token prompt has nothing to reuse.
4. **Measure the hit rate, not the cache size.** It's the only number that says whether any of this works — `cachedContentTokenCount` / `usage_metadata.cached_tokens` on Gemini, `usage.cache_read_input_tokens` on Anthropic. OpenHands treats it as its **top-level metric**, and the reason is the price: cached $0.30 vs uncached $3.20 per MTok, roughly 10×. `[self-reported]`

#### 🧊 Precomputed KV caches (CAG)

Move the prefill cost offline. Correct when knowledge is stable and small enough
to hold. A real architecture, not a micro-optimization.

- **[Don't Do RAG: When CAG Is All You Need (WWW 2025)](https://arxiv.org/html/2412.15605v1)** · `HotpotQA generation time: 0.85s vs 9.25s (small), 1.66s vs 28.8s (medium)` · `[measured]`
  Precompute `KV-Encode(D)` offline once, then answer queries against the cached states — no retrieval at query time, and no chance of retrieving the wrong chunk. Accuracy *exceeds* sparse/dense RAG on several settings (0.7696 vs 0.6652). Cache reset is a truncate of appended query tokens, not a reload from disk.
- **[TurboRAG](https://arxiv.org/pdf/2410.07590)** — the same idea per *document*: precompute each chunk's KV offline, retrieve cached KV directly for prefill. Removes the repeated recompute that dominates RAG TTFT, since KV cost is quadratic in sequence length. Costs a CPU→GPU transfer; independent attention plus reordered positions costs ~4–6% accuracy until fine-tuned, then <1%. `[measured]`
- **[ACC — adaptive contextual compression for CAG](https://arxiv.org/html/2505.08261v1)** — **−45% context window occupancy**, sub-700ms inference, +5–10% BERTScore over sparse/dense RAG. The hybrid CAG-RAG variant adds 1–2 BERTScore points for 5–10% latency. `[measured]`
  ⚠️ **And the cost side CAG marketing omits:** on HotpotQA, standard CAG needs **18,000MB** against sparse RAG's 12,000MB — the *most* memory of any arm tested. Compressed CAG (ACC) brings that to 13,000MB. Preloading trades per-query cost for resident memory, permanently.


## Leg 2 — Output

What you get billed for, at 5–25× the input rate. Ordered the same way: audit
the invisible spend, budget it, reason less about it, constrain its shape, write
it cheaply, and cut it at the tool boundary.

### 📐 Audit

Start here. Most of the output bill is invisible.

- **[Thinking tokens are billed at the output rate](https://getnadir.com/blog/extended-thinking-tokens-output-billing)** — $25/M vs $5/M input on Opus-class. Worked example: 8,200 thinking tokens added **$0.205 to a $0.033 call — 7.2× total, identical visible response.** Most teams have never calculated reasoning overhead as a share of output spend. `[measured]`
- **[The hidden cost of "cheap" AI](https://dev.to/max_quimby/the-hidden-cost-of-cheap-ai-why-budget-reasoning-models-actually-cost-6x-more-3e0)** — thinking tokens are **>80% of total output cost**. Removing them from the analysis raises the price↔actual-cost correlation from 0.563 to 0.873 and eliminates 70% of rank reversals. Gemini 3 Flash burned 208M thinking tokens on GPQA. *This is the single most important table in the output half.* `[measured]`
- **[Brevity is the soul of sustainability (ACL 2025)](https://aclanthology.org/2025.findings-acl.1125/)** — the taxonomy everything else builds on: **MinAns** (minimal answer) vs **Irrel** (irrelevant, hallucinated, repeating). MINANS framing ≈ −60% output tokens, explicit length prediction −53%. Annotated dataset released. `[measured]`
  🔋 **This is also the paper that priced output length in energy**: appropriate length-reduction prompts achieve **25–60% energy reduction with quality preserved**, and the six-category annotation shows the minimal answer is only **~42%** of a typical response. Its key structural finding explains the whole [pitch](#what-you-actually-save): *energy depends largely on output size, not on task complexity or type* — because output is generated sequentially and input is not. [Dataset + code](https://github.com/sohampoddar26/LLM-brevity).
- **[Verbosity Compensation Behavior (UncertaiNLP 2025)](https://aclanthology.org/2025.uncertainlp-main.14/)** — models trained toward brevity get *worse* at concise answers. Distilling Mistral→GPT cut verbosity compensation from 63.81%→31.79% down to 16.60%. **Brevity can be a training artifact, not a prompt property.** `[measured]`
- **[Computational Challenges in Token Economics](https://arxiv.org/pdf/2605.17410)** — treats tokens as economic primitives; frames the granularity / real-time / optimality tension. Good survey of the vocabulary. `[measured]`
- **[Energy use of AI inference (Joule / Microsoft Research)](https://www.cell.com/joule/fulltext/S2542-4351%2826%2900114-5)** — the calibration for every energy claim: frontier-scale inference is a median of **0.31 Wh/query** (IQR 0.16–0.60), and widely-cited public estimates **overstate it by 4–20×** because they assume non-production deployments. The number that matters here: **reasoning queries (~5,000 output tokens) raise energy ~13×.** Also notes model, serving, and hardware gains could cut per-query energy **8–20×** — so this is a lever, not a constraint. `[measured]`
- **[The Energy Cost of Reasoning](https://arxiv.org/pdf/2505.14733v2)** — direct measurement of test-time compute. Reasoning traces average **7,845 output tokens per query** and a ~258MB KV cache even at 7B. The result worth internalizing: going 1.5B → 7B *base* gives **+16.8% accuracy and −40.1% energy**, while adding reasoning traces to the 1.5B gives a similar **+17.3% accuracy for +57.4% energy**. Same accuracy, opposite energy sign — the lever is *how* you buy it. `[measured]`
- **[Measuring Energy Consumption of LLM Inferences (SIGMETRICS)](https://dl.acm.org/doi/10.1145/3788882.3788890)** — independent measurement across transformer families up to DeepSeek V3/R1, consistent with the above. Use it to sanity-check any energy figure you're quoted. `[measured]`
- **[From Tokens to Watt-hours](https://arxiv.org/abs/2607.26571)** — an analytical estimator that decomposes inference energy into compute, parameter access, **KV-cache write, and attention read**. That decomposition is why [caching](#%F0%9F%92%BE-cache) is an energy lever and not only a cost lever: the KV work you skip is work you don't pay for in joules either. `[measured]`

### 🎯 Budget

Give the model a number. Then check it obeyed.

- **[TALE / Token-Budget-Aware Reasoning (ACL 2025)](https://aclanthology.org/2025.findings-acl.1274/)** · [`GeniusHTX/TALE`](https://github.com/GeniusHTX/TALE) · `[measured]`
  Estimate your own budget, then reason against it. **−67% output tokens, −59% expense, <3% accuracy drop** across seven datasets. On GSM8K accuracy went **up** 81.35% → 84.46% while output fell 318 → 77 tokens. On GSM8K-Zero: **252.96 → 22.67 tokens at 98.72% accuracy.**

  > ⚠️ **The budget-inversion result.** A 50-token budget cut 258 → **86**
  > output tokens. A *tighter* 10-token budget produced **157** — nearly double —
  > plus >20% relative accuracy loss. Models ignore budgets that are too tight
  > and revert to long reasoning. Every "just cap it" advice skips this.

- **[Length-capped prompting (ACL 2025)](https://aclanthology.org/2025.findings-acl.1125/)** — "answer within X words", few-shot length exemplars, MINANS framing. The cheapest entry here; start before reaching for TALE. `[measured]`

### 🧠 Reason less

Not "stop reasoning" — **stop reasoning uniformly about easy problems.**

- **[Chain of Draft](https://arxiv.org/abs/2502.18600)** · [`sileix/chain-of-draft`](https://github.com/sileix/chain-of-draft) · `[measured]`
  "Think step by step, but only keep a minimum draft for each thinking step, 5 words at most." **As little as 7.6% of CoT tokens.** GPT-4o: 205.1 → **43.9** tokens, 4.2s → **1.0s**, accuracy 95.4 → 91.1%. On Claude 3.5 Sonnet / date understanding: 172.5 → **31.3** tokens, accuracy 87.0 → **89.7%** — shorter reasoning was *more* accurate.

- **[Concise Chain-of-Thought](https://arxiv.org/html/2401.05618v3)** — −48.70% response length, −22.67% per-token cost. **And the honest cost:** −27.69% accuracy on math for GPT-3.5. The originating paper's point is that verbose CoT convention rests on "anecdotal rather than empirical evidence." `[measured]`
- **[Concise Thoughts (2407.19825)](https://arxiv.org/abs/2407.19825)** — CCoT on GSM8K: 36.01% → **41.07%** accuracy while output fell 99 → 71 words. Also introduces HCA/SCA/CCA, metrics that score correctness *accounting for* conciseness. `[measured]`
- **[NoWait (EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.394.pdf)** — suppress `Wait` / `Hmm` logits at inference. CoT trajectories −27% to −51%. QwQ-32B on AIME: 15,240 → 10,548 tokens with accuracy **rising** 67 → 68. Reflection markers aren't load-bearing. `[measured]`
- **[MUTO — Think Better, Not Longer (ACL 2026)](https://aclanthology.org/2026.acl-long.1386.pdf)** — per-token **marginal utility** via log-prob gain on the ground truth. −87.1% tokens at 1.5B *and* +2.3% accuracy; 7,815 → 1,544 at 7B for −0.1%. The strongest accuracy-neutrality claim here, and a principled metric the prompt-only methods lack. `[measured]`
- **[TRS — Thinking with Reasoning Skills (ACL 2026)](https://aclanthology.org/2026.acl-industry.154.pdf)** — reuse *distilled procedural skills* instead of forcing shorter reasoning. Beats TALE/NoWait/CoD on hard tasks (~45–80% uplift on the hardest GPT-OSS sets). Note it can lose money: GPT-OSS-120B gained +4.1 pass@1 at **+4.8% cost** because the prompt grew. `[measured]`
- **[caveman](https://github.com/JuliusBrussee/caveman)** — output-side prose compression. States its own boundary better than most: *"Caveman only affects output tokens — thinking/reasoning tokens are untouched. Caveman make mouth smaller. Caveman no make brain smaller."* Ships `caveman-compress` for memory files (~46% of CLAUDE.md, permanently) and a three-arm `evals/` harness that explicitly refuses the "verbose vs skill" comparison as *cheating* — comparing to verbose Claude conflates the skill with generic terseness. ⚠️ **Advertised −65%, independently measured −8.5%.** `[measured]/[asserted]` — audit is measured, the tool's own headline is not
- **[CAVEWOMAN (Adobe Research)](https://arxiv.org/abs/2606.24083)** — cited by caveman as measuring caveman-style output compression across 8 models, 5 datasets, 5 compression levels at 1.4–2.4× cost cut, up to 3×. **Not independently verified here** — treat as self-reported until you read the paper. `[self-reported]`

### 🧾 Constrain

A schema is usually smaller than a paragraph, and it removes the preamble tax.

- **[Structured outputs vs tool use vs prefills](https://dev.to/pavelespitia/structured-outputs-vs-tool-use-vs-prefills-getting-json-out-of-claude-in-2026-5fi0)** — the decision rule worth memorizing: *extracting fields from text → structured outputs; JSON passed to the next tool → tool use; forcing a label → enum tool.* ⚠️ Also: assistant-turn prefills now **400** on Claude 4.6+. If you're still prefilling `{`, one model-string bump breaks your code. `[asserted]`
- **[Terminating tool calls](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/structured-output.ts)** — end the agent turn on the tool call instead of paying an extra inference pass to narrate the result. Small, concrete, widely unknown. `[self-reported]`
- **[Claude output control](https://www.blockchain-council.org/claude-ai/claude-output-control)** — `max_tokens` as a hard cap, schema-driven JSON reports, `tool_choice` forcing, and "when calling tools, output only tool arguments; no commentary." `[asserted]`

### ✏️ Edit cheaply

The edit protocol is a token decision, not a formatting preference.

- **[AdaEdit / FuncDiff / BlockDiff (ACL 2026)](https://aclanthology.org/2026.findings-acl.1483)** — standard diffs *increase* failure rates: "fragile offsets and fragmented hunks make generation highly unnatural for LLMs." Structure-aware block-level diffs match full-code accuracy at **>30% lower cost and latency** on long-file edits; adaptive selection beats any fixed format. `[measured]`
- **[BlockDiff (Cognition)](https://cognition.com/blog)** — block-level snapshots built for agents as a first-class file format. `[self-reported]`
- **[SWE-Edit](https://arxiv.org/html/2604.26102v1)** — the rare paper where token reduction *and* quality improved together. Viewer returns on average **39.7%** of the requested file (60.3% less code surface); combined with an adaptive editor, non-cached main-agent input **276.7k → 181.3k (−34.5%)**, total cost −17.9%, and edit success **93.4% → 96.9%**. `[measured]`

### ✂️ Prune output at the tool boundary

- **[rtk](https://github.com/ai-skynet-labs/reduce-tokens)** — transparent Bash-output rewrite, claimed 60–90%. ⚠️ **Measured +7.6% cost** at low reasoning effort (p=0.004), ±0% at high. Note its own honest limit: built-in Read/Grep/Glob bypass the hook entirely. `[negative]`
- **[token-efficiency skill (undefdev)](https://github.com/undefdev/token-efficiency)** — `jq`/`yq`/`awk` over dump-and-read, `ast-grep` over broad search, `git --stat`/`--name-only`, quiet flags, hash-based change detection. Carries a **sunset notice**: it exists because current agents haven't internalized efficient tool use, and will be retired as they do. Steal that framing. `[self-reported]`
- **[Cognition's retriever lessons](https://cognition.com/blog)** — a trained model *always* writes tests for every tiny change; give it a measurable target instead. See [Leg 3](#leg-3--lifetime). `[measured]`

---

## Leg 3 — Lifetime

What you emit becomes context that every future session pays for. Ordered by
when you can act: don't build it, prune what you built, bound the goal you prune
toward, and hold a retention bar so pruning doesn't eat your guards.

> **You emit context, you don't just spend it.** Every line an agent generates is
> a charge on every future session that touches that subsystem. Review artifact
> cost the way you review API cost.

### ⬇️ Build less

Prospective. Don't emit the artifact in the first place.

- **[ponytail](https://github.com/DietrichGebert/ponytail)** — "the laziest senior dev." `<input type="date">` instead of a library install plus wrapper component. ⚠️ **Advertised −54% code / −20% cost; independently measured −15.4% code (p=0.088) and −10.3% cost (p=0.004).** Credit where due: they found and documented a **contamination bug in their own harness** (a SessionStart hook firing in the baseline), rebuilt against headless Claude Code on a real repo, and published the smaller number. Model-dependence caveat: works on Claude-class, transfers poorly to small local models. `[measured]/[self-reported]` — audit is measured, the remaining benchmarks are the authors' own
- **"Follow YAGNI, prefer one-liners"** — a **seven-word prompt** measured −33% code, −21% cost, −30% time against the same baseline, matching ponytail on cost and time. It was also the only arm that wrote an unsafe function (dropped a path-traversal check once in four runs). **The cheapest intervention is often a sentence** — and the cheapest intervention is not always the safest one. `[measured]`
- **[token-saviour](https://github.com/vagkaratzas/token-saviour)** — the thesis as a tool: classify the task by *layer* and route to the per-layer winner (serena for code reads, rtk for command output, caveman for prose, ponytail for code). ⚠️ Its benchmark (−69.6% stacked) **directly contradicts** JetBrains' rtk result (+7.6%). Different harness, different cost basis. Grade `⚠️ contested` and read both. `[self-reported]`

### 🧹 Prune what you already emitted

Retrospective. Harder, and the highest-leverage work in this list.

- **[test-audit (OpenClaw)](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md)** · `−400k LOC tests, coverage held` · `[self-reported]`
  Three modes: an **authoring gate** that rejects a new test before it is written, a focused audit mode, and a campaign mode that prunes one subsystem's whole test surface. Contributes four separable mechanisms, each reusable on its own:

  1. **Authoring gate** — four questions before adding a test; a missing answer means don't add it yet. Prevents the bloat from accruing rather than cleaning up afterward.
  2. **Junk patterns** — assertion-free coverage probes, self-comparisons, copied fixtures, exact source/import/string greps, mocks that implement the asserted behavior, negative controls that pass for an unrelated reason, tests whose only purpose is preserving test-only exports.
  3. **Candidate evidence** — seven fields recorded *before* editing. **A missing field means the candidate is not ready for deletion.** A deletion gate shaped exactly like this repo's evidence rubric.
  4. **Anti-gaming guardrail** — *"do not convert uncertain candidates into cleanup to increase deletion counts."*

- **[Why models over-test](https://github.com/openclaw/openclaw/blob/main/.agents/skills/openclaw-testing/SKILL.md)** — the sibling skill: *"Do not add tests that merely mirror reversible, low-impact implementation changes."* David's Cramer's one-liner on the original post nails the failure mode: *"they also love rewriting tests when they change code as if the reason for those tests in the first place wasnt to prevent regressions."* `[asserted]`
- **[Commit archaeology as evidence](https://git.mineracks.com/openclaw/openclaw/commits/commit/61dc7ac67994b8a8ae370d8d90200e87746d1b22)** — a single burst in the history reads `test: expand X coverage` twelve times. Commit-message histograms are a free, retrospective audit of what your agents have been doing to your codebase. `[measured]`

> ⚠️ **Grade this claim honestly.** ~400k LOC with coverage "not much changed" is a
> maintainer report on X: no n, no harness, no baseline, no independent
> replication. And **coverage is exactly the metric that can be gamed** — deleting
> 400k lines while coverage holds flat is consistent with the skill's own claim
> that those tests were re-asserting source, but it also means coverage is a weak
> proxy for value retained. The real argument is the retention bar, not the
> coverage number. Compare it against the [ledger](#token-ledger): one is a
> 1.2M-view tweet with no methodology, the other is a paired A/B with p-values.

### 🚪 Bound the goal

**If you just tell an agent to clean up, it will stop far too early. Give it an ambitious, measurable goal:** *"remove 20% of the least useful tests while maintaining code coverage within 2%."*

This is not a quirk of that skill. It is the mirror image of the
[budget-inversion result](#%F0%9F%93%90-budget), and they are the same law:

| | Open-ended constraint | Bounded constraint |
|---|---|---|
| **Output** | "be concise" → −60%, then plateaus | "use less than 50 tokens" → 258 → 86 |
| **Artifact** | "clean up the tests" → **stops far too early** | "−20%, hold coverage within 2%" → **−400k LOC** |

Models undershoot open-ended optimization targets and overshoot tight ones.
**Both are fixed by the same move: replace an open-ended goal with a measured,
bounded one.**

- **[skill-cleaner (steipete/agent-scripts)](https://github.com/steipete/agent-scripts/blob/main/skills/skill-cleaner/SKILL.md)** — the input-side version: audit live skill budget, find duplicates, compact descriptions. Since a skill's description loads **always** (~100 tokens each), compacting them is pure savings with no capability loss. Preserves trigger nouns — *product, tool, action, object* — so the skill still fires. `[self-reported]`

### 🪞 Retention bars — don't delete without one

An aggressive pruning agent will delete real guards unless you tell it what to
keep. From test-audit, and generalizable to any artifact:

> **"Static or slow is not a deletion reason."**
> **"A test that would break under behavior-preserving refactoring is asserting
> implementation, not behavior."**

Keep anything that independently enforces a **public API, plugin SDK, protocol,
config, migration, storage, security, platform default, prompt-byte,
generated cross-language, package, release, or architecture contract.** Plus call
ordering when it is observable behavior, and regressions with credible failure
modes. "Source inspection" counts when it fails on a contract change and survives
an identifier-only refactor.

This is also the general form of the [microcompact failure](#%F0%9F%97%91%EF%B8%8F-delete):
deletion without a retention bar is a regression with extra steps.

---

## Serve-side: cost and latency, *not* token count

Speculative decoding is the case that forces this distinction. It is **lossless**
— identical output distribution — and cuts cost per token ~60% and latency 2–3×.
**It reduces zero tokens.** Every "token efficiency" list files it as a win, which
is a category error.

So every entry carries three numbers, not one:
`Δ tokens-in │ Δ tokens-out │ Δ $ / Δ wall-clock`

Anything that only moves the third column is `⚡ serve-side`.

- **[Speculative decoding (ICML 2023)](https://proceedings.mlr.press/v202/leviathan23a/leviathan23a.pdf)** — 2–3× with identical outputs, no retraining. `[measured]`
- **[SPIRe](https://arxiv.org/html/2504.06419v1)** · `[measured]`
- **[Decoding Speculative Decoding (NAACL 2025)](https://aclanthology.org/2025.naacl-long.328.pdf)** — draft-model selection matters; up to 56% latency reduction needed just to reach parity. `[measured]`
- **[Speculative decoding economics (Red Hat)](https://developers.redhat.com/articles/2026/06/12/how-speculative-decoding-delivers-faster-llm-inference)** — 60% cost reduction, same hardware. ⚠️ Only pays when decoding is memory-bound; with low acceptance length it can be *slower*. `[measured]`
- **[smolagents](https://github.com/huggingface/smolagents)** — agent logic in <1,000 lines, and CodeAct-style code-as-action uses **30% fewer steps**. Fewer *calls* is a latency win, not a token win. `[measured]`
- **[Cognition: context caps](https://cognition.com/blog/dont-build-multi-agents)** — enabled the 1M-token beta while capping actual usage at 200k. Environment design: give the model the experience of ample runway without changing the effective working set. `[self-reported]`

---

## Interaction matrix

Bidirectional, tridirectional minimalism has real **contradictions**. They are
the reason this list is worth reading rather than skimming.

| Pull | Toward | Why they fight |
|---|---|---|
| Compress input | ↔ Cache input | Compression rewrites the prefix → every call is a cache miss. Naive compression can be **net negative**. [CAPC](https://arxiv.org/html/2607.15516v1) models it; the fix is cache-aware compression, not "compress less." |
| **Delete context** | ↔ **Cache the prefix** | **Same collision, arrived at from the other side.** Anthropic: *"tool clearing will invalidate your cache if your prefixes contain your tools."* Thinking-block clearing: kept → cache preserved, cleared → cache invalidated at that point. Context editing still wins overall (**+29% performance, −84% tokens** on a 100-turn eval) — but you are choosing a regime, not adding an optimization. `clear_at_least` exists as a knob precisely because the tradeoff isn't free. |
| Shorter reasoning | ↔ Math accuracy | CCoT −27.69% on math (GPT-3.5); short reasoning hurt small and medium models too. Model- and task-dependent, not universal. |
| Tighter budgets | ↔ Budget compliance | 10-token budget → **157** output tokens, worse than a 50-token budget. Non-monotonic. |
| Enable thinking everywhere | ↔ Invisible bill | 7.2× cost, identical visible response, no dashboard line item. |
| Diff outputs | ↔ Edit robustness | find-replace is cheap but whitespace-brittle; whole-file rewrite is robust and expensive. [SWE-Edit](https://arxiv.org/html/2604.26102v1) learns to *choose per task* rather than pick a side. |
| Clear tool results | ↔ Durable memory | [microcompact](https://github.com/anthropics/claude-code/issues/57788) silently deleted user memory and the model could not self-diagnose. |
| Teach brevity via few-shot | ↔ Input cost | Exemplars load every call. caveman adds ~1–1.5k input tokens per turn for the skill itself — net-negative on already-terse work. |
| Fewer tools | ↔ Tool accuracy | Direction of effect is *contested*: Tool Search Tool reports selection improving 49% → 74%, but the [LSP measurement study](https://arxiv.org/pdf/2608.13568) found LSP tooling **costing** +6% (Opus) to +118% (Sonnet) on symbol-localization. Different mechanisms, both can be true. |
| **Prune the artifact** | ↔ **Future debug cost** | **Delete a guard that mattered → bug → more sessions → more lifetime context than you saved.** The lifetime axis has the *same* re-fetch trap as compression: **tokens-per-task, not tokens-per-edit.** |
| Bounded goal | ↔ Gaming | "−20% while holding coverage within 2%" is gameable both ways: pick the easy 20%, or delete only redundant tests and stop. Needs an independent guard metric. |
| Graph retrieval | ↔ Ingestion cost | GraphRAG-global spends **331k prompt tokens** to answer what vector RAG answers in **879**. The cost moves from the query to the index — same trade as compress ↔ cache, on a different clock. [LazyGraphRAG](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost) exists because of this row: same graph quality, 0.1% of the index cost. |
| Graph retrieval | ↔ Loop length | In agentic RAG the dominant cost driver is **sequential tool calls**, not retrieval volume — a 5-call session burns ~250k tokens vs 36k for a 3-call session *regardless of documents retrieved* ([ACL 2026](https://aclanthology.org/2026.gem-main.40)). Optimizing the retriever while the loop grows is optimizing the small term. |
| Structured memory | ↔ Recoverability | Extraction at ingestion fixes a schema before the query is known; anything discarded can't be recovered later. [True Memory](https://arxiv.org/html/2605.04897v1) argues ingestion-time extraction is the wrong primitive and reports higher recall from a single SQLite file. The counter-case — graphs win multi-hop and time — is real. |

> **The last two rows are where this list argues with itself.** test-audit's own
> technique invites the failure the repo exists to catch. Flagged, not resolved.
> The graph rows have the same shape: the cheapest representation at query time
> can be the most expensive one to build.

---

## 🧮 Break-even

The matrix above says which levers conflict. This says which one wins, as
arithmetic. Everything is expressed in **ratios**, so it survives a price change;
the ratios themselves are stamped at the bottom.

### Notation

| Symbol | Means |
|---|---|
| `c` | context tokens sent per turn |
| `o` | output tokens generated per turn |
| `r` | output price ÷ input price (the multiplier) |
| `h` | cache hit rate — fraction of `c` served from cache |
| `w` | cache-write premium (Anthropic: 1.25× base input) |
| `α` | size after compression, as a fraction of `c` |
| `p` | input price per token |

Per-turn cost, ignoring the one-time write, is `c·p·[h·0.1 + (1−h)] + o·p·r`.

### 1. When does output dominate?

`o·r > c`, i.e. **`o > c / r`**. At `r = 5` and a 20k-token context, output
takes over above 4,000 output tokens. Reasoning models cross that line
routinely — which is why [Leg 2](#leg-2--output) exists at all. If you are
optimizing input on a reasoning workload, you are optimizing the small term.

### 2. Is one cache write worth it?

Writing costs `w` instead of `1` — an *extra* `w − 1 = 0.25` per token, once.
Each hit then saves `0.9` per token. So a write pays for itself once

**`0.9·h > w − 1`** → **`h > 0.28`**

At any hit rate above ~28%, **the very next turn repays the write.** Below that,
count the turns: `T = 1 + (w − 1) / (0.9·h)`.

| Hit rate `h` | Turns to repay (w = 1.25) |
|---|---|
| 0.9 | **1.3** |
| 0.5 | 1.6 |
| 0.3 | 1.9 |
| 0.1 | 3.8 |

**The write premium is never the thing to optimize.** What kills you is
*invalidation*: if `h → 0` while you keep writing, you pay `1.25 ×` forever
instead of `0.1 ×` — **12.5× worse than a working cache, and 1.25× worse than
having no cache at all.** A broken cache is worse than none.

### 3. Does compression pay if it breaks the cache?

Compressing to `α·c` with no cache costs `α·c·p`. Leaving it cached costs
`c·p·[h·0.1 + (1−h)]`. Compression wins when:

**`α < 1 − 0.9·h`**

| Hit rate `h` | Compression must remove |
|---|---|
| 0.9 | **>81%** |
| 0.7 | >63% |
| 0.5 | >45% |
| 0.2 | >18% |
| 0 | >0% (always wins) |

This is [CAPC](https://arxiv.org/html/2607.15516v1)'s finding as a formula, and
it is the single most useful inequality in the list. **At a 90% hit rate,
compression has to delete four fifths of the prefix before it pays for the cache
it destroyed.** Check `h` before you check your compression ratio — it is the
difference between a win and a regression.

### 4. Is a bigger context worth it?

Adding `Δc` input tokens to prevent one retry of `o_retry` output tokens:

`Δc < o_retry · r`

Adding `Δc` to avoid `n` retries: `Δc < n · o_retry · r`.

At `r = 5`, a 500-token retry justifies **2,500** extra input tokens. Beyond
that the context is costing more than the failure it prevents — before counting
[context rot](#%F0%9F%93%8F-effective-context), which subtracts from the benefit
without appearing in the equation.

### 5. Is reasoning worth its tokens?

A thinking pass of `k` tokens costs `k·p·r`. Worth it when `q·C > k·p·r`, where
`q` is the probability it converts a failure and `C` is the cost of that
failure. Enabled uniformly across `N` calls, the waste is
`(1 − f)·N·k·p·r` where `f` is the fraction that needed it. Enterprise case
studies put `f` near 0.4, so **~60% of a uniform reasoning budget buys nothing.**

### 6. Multimodal equivalence

Same pixels, ~5× spread. Per image:

| Provider | Formula | 1024×1024 |
|---|---|---|
| Gemini | 258 flat ≤384px; else 258/tile | **258** |
| GPT-4o / 4.1 | `85 + 170 × tiles`, tiles = ⌈w/512⌉·⌈h/512⌉ | **765** |
| GPT-4o `detail: low` | flat 85 | **85** |
| Claude (standard) | ⌈w/28⌉·⌈h/28⌉, cap 1,568 | **~1,400** |
| Claude (high-res tier) | same, cap 4,784 | **~1,400** |

A screenshot is worth `1,400 / (4 chars/token) ≈ 5,600 characters` of text on
Claude. An accessibility-tree snapshot of the same page measured **121 tokens
against 15,704** for the screenshot — **129.8×** cheaper and often more
precise, because the tree is the structure rather than a rendering of it.

### Ratios used, and when to re-check

| Constant | Value | Stability |
|---|---|---|
| `r` (output ÷ input) | 4–5 for current frontier text models | **volatile** — re-check on every model release |
| cache read | 0.1 × input | structural, stable |
| cache write `w` | 1.25 × input | structural, stable |
| Gemini image ≤384px | 258 tokens | stable until tiling rules change |
| Claude standard cap | 1,568 visual tokens | stable; high-res tier is 4,784 |

`[measured]` for the structural constants and the image formulas; `[self-reported]`
for the `r = 4–5` band, which is a snapshot and belongs to whoever's price sheet
you're on. **Re-derive the constants, not the formulas** — the inequalities are
the durable part.

> **The two numbers that decide almost everything:** your cache hit rate `h` and
> your output-to-input ratio `r`. Instrument both before optimizing anything
> else in this list.

---

## Laws

**Input**

1. Context is a budget, not a bucket. Spend it like money.
2. The cheapest token is the one you never send.
3. Identifiers beat payloads. A file path is ~12 tokens; the file is 4,000.
4. Every tool schema is a permanent tax on every turn.
5. Compress and cache are antagonistic. **So are delete and cache.** Pick a regime deliberately, and instrument it.
6. Advertised context ≠ effective context. Benchmark yours.
7. **Cache hit rate is the primary metric, not cache size.** Nothing here is verifiable without it, and at ~10× the price difference it is the largest single lever on the input bill.
8. **Deletion and caching are the same lever pointed opposite ways.** Clearing tool results trades every-turn cost for once-per-invalidation cost. Decide with the hit rate in front of you, never with the token count.

**Output**

9. Output tokens are 5× the price. Treat them as the scarce resource.
10. **Reasoning tokens are output tokens. Instrument them, or they're free money for your provider.**
11. A budget you can't meet isn't a budget — it's a suggestion the model overpays on.
12. Prefer a schema to a paragraph; a tool call to a sentence.
13. Ask for the smallest thing that answers the question. Then check that it did.
14. A diff is not a rewrite. Edit protocols are a token decision.
15. Verbosity is trainable, which means brevity is sometimes an artifact, not a fact. Measure per model.
16. Token count, latency, and dollars are three different numbers. Know which one you reduced.

**Lifetime**

17. **You emit context, you don't just spend it.** Review artifact cost like API cost.
18. **An open-ended cleanup goal will be undershot. Bound it** — name the target and the guard metric.
19. **A deletion without a retention bar is a regression with extra steps.** State what each thing independently protects before removing it.
20. **Never convert uncertain candidates into cleanup to hit a number.** This applies to PRs and to ledger entries alike.
21. Optimize tokens-per-**task**, not tokens-per-request or per-edit. Re-fetching is the hidden cost on all three legs.
22. **Don't pay an LLM to summarize your index when a join would do.** Graph quality does not require community summarization — the cheapest systems here reach it with deterministic structure.
23. **One change, three budgets.** Money, wall-clock, and joules are all metered per token, so reducing tokens is the rare optimization with no trade-off face. When you find one that trades one budget for another — speculative decoding, precomputed KV — say which one you spent.

---

## Token ledger

Advertised vs. independently measured. Same harness for the first three rows:
Docker-sandboxed SkillsBench tasks, Claude Code headless, paired A/B, pinned
model, real billed trials, significance tests
([JetBrains, 2026](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested)).

| Tool | Advertised | Measured | Quality |
|---|---|---|---|
| [`caveman`](https://github.com/JuliusBrussee/caveman) | −65% output tokens | **−8.5%** (86 tasks, sign test p=0.82) | flat |
| [`rtk`](https://github.com/ai-skynet-labs/reduce-tokens) | −60…90% | **+7.6% cost** at low effort (p=0.004, 425 trials), ±0% at high | tie |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | −54% code, −20% cost | **−15.4% code** (p=0.088), **−10.3% cost** (p=0.004), −11% time | indistinguishable (65/80 identical) |
| [`test-audit`](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md) | −400k LOC tests | *no independent replication* — self-reported, coverage-only guard | reportedly held |

Head-to-head against ponytail's own rebuilt benchmark
([curviate](https://curviate.com/blog/ponytail-vs-caveman)):

| Arm | Code | Tokens | Cost | Time | Safe |
|---|---|---|---|---|---|
| `ponytail` | −54% | −22% | −20% | −27% | 100% |
| `caveman` | −20% | **+7%** | **+3%** | +2% | 100% |
| *"Follow YAGNI, prefer one-liners"* (7 words) | −33% | −14% | −21% | −30% | **95%** |

**Three separate tools, one harness, two of three failed to deliver** — and one
was *more expensive*. That is not an anecdote; that's a reproducible pattern.

**Read this table before buying anything in this list.** And if you run one of
these tools yourself, publish the number. The gap between what a tool claims and
what the bill says is currently the least-measured quantity in the entire field.

### Provenance, when you have it

`measured` doesn't require a lab. It requires a **baseline and a method**. Stamp
what you actually ran:

```
model: claude-sonnet-5 · harness: Claude Code 2.1.201 · date: 2026-07
n: 80 paired · p=0.004 · quality: 65/80 identical
```

Anything without a stamp is `[self-reported]`, however large the number.

---

## Open problems

Real gaps. Nobody has measured these.

1. **Where does a retention bar stop being worth its tokens?** test-audit's
   retention bar is prose in a skill: it costs tokens on every run and slows
   every deletion. Obviously worth it at 400k LOC. Where's the threshold?
2. **Is there a quality-preserving minimum for any artifact?** ponytail and CoD
   both found *accuracy rising* as output shrank. Is there a floor, and how do
   you know you've hit it without a benchmark?
3. **Does lifetime bloat compound?** If token 3 of a test file costs more than
   token 1 (because later tokens only get read when the first fails), the
   lifetime curve isn't linear and every deletion decision changes.
4. **What is the *correct* unit for compression loss?** tokens-per-task is
   better than tokens-per-request, but it requires knowing the re-fetch rate,
   which is unmeasured almost everywhere.
5. **Nobody has an independently audited context-window profiler.** Every tool
   in [Leg 0](#leg-0--measure) is `[self-reported]`.
6. **Is per-model brevity tuning worth it?** Verbosity compensation suggests
   conciseness is model-specific. Whether one ruleset can serve three model
   families, or needs to be three rulesets, is unmeasured.
7. **Does bounded-goal cleanup invite reward hacking at scale?** The 400k number
   came with a coverage guard that coverage-gaming could satisfy.
8. **What is the break-even query volume for a graph index?** ContextRAG says it
   is "most attractive for low- and medium-query workloads, especially when
   corpora are re-indexed frequently" — but nobody has published the curve. You
   would need `index_cost / (per_query_vector_saving × queries)` against corpus
   churn, and no framework reports the first term by default. GraphRAG's own
   indexing-cost tracking was a [user feature request](https://github.com/microsoft/graphrag/issues/1153),
   not a default.
9. **Is graph structure or extraction the thing that matters?** ContextRAG and
   TERAG both drop LLM-written edges and keep the graph, with large token wins.
   Nobody has cleanly separated "structure helps retrieval" from "LLM-written
   structure is expensive," which is why the token column and the relevance
   column disagree so consistently across the [table above](#%F0%9F%95%B8%EF%B8%8F-graph-engineering).
10. **Where is the delete↔cache crossover?** Context editing wins on tokens *and*
    performance in Anthropic's own eval, but clearing invalidates the prefix — and
    nobody has published hit rate *before and after* enabling it. Without that
    pair of numbers, "should we turn on context editing?" has no evidence-based
    answer outside one vendor's internal benchmark.
11. **Is there a hit rate above which preloading always wins?** CAG is ~10–17×
    faster at query time but needs *more* resident memory (18GB vs 12GB on
    HotpotQA) and a corpus stable enough to precompute. Break-even depends on
    query volume, corpus churn, and hit rate simultaneously — three variables, no
    published curve.
12. **Semantic caching is deliberately absent.** It saves more than any mechanism
    in this list and it is the one most likely to return a confidently wrong
    answer. Omitted rather than uncritically included; somebody should measure its
    false-hit rate.

---

## Anti-patterns

Each one names a **default that shipped unmeasured**, with a receipt.

1. **Eagerly-loaded tool schemas.** `tools/list` is a flat payload injected every
   turn; no partial-loading primitive exists in the spec, so every workaround
   lives above it. [GitHub MCP: 91 tools, ~17.6k tokens/session](https://www.atlassian.com/blog/developer/mcp-compression-preventing-tool-bloat-in-ai-agents).
   *Worst single tool observed: 557,766 average output tokens; 16 tools exceed 128k* ([MSR](https://www.microsoft.com/en-us/research/blog/tool-space-interference-in-the-mcp-era-designing-for-agent-compatibility-at-scale)).
2. **Uncleared tool results.** A turn-3 result still costing 8k tokens at turn 20.
3. **Invisible reasoning spend.** 7.2× total call cost, unchanged visible
   response, no line item on the dashboard.
4. **Uniform reasoning budgets.** Thinking enabled on 100% of calls when ~60%
   don't need it — 40–70% of the output bill, wasted.
5. **Duplicated instruction files.** The same three rules pasted into
   `CLAUDE.md`, `.cursor/rules`, and `copilot-instructions.md`, loaded every turn.
   Measure the overlap, not just the total.
6. **Whole-file rewrite as default.** Robust and expensive, chosen without
   conditioning on scope. Cost is real; so is the whitespace-mismatch failure.
7. **Dump-and-read retrieval.** Raw output into context where `jq` or `--stat`
   would do.
8. **N× self-consistency sampling.** An accuracy method that multiplies the most
   expensive resource. Measure the marginal gain per sample.
9. **Unrouted vector-only retrieval.** No rerank, no citations, no audit trail.
   Also see the [RAG-is-dead roundup](https://www.forbes.com/councils/forbestechcouncil/2026/07/09/rag-didnt-die-it-moved-up-the-stack) —
   retrieval moved up the stack; stuffing pays ~1000× for degraded recall.
10. **Unbounded background agents.** 14 agents × ~80k tokens, zero usable output
    ([claude-code #25714](https://github.com/anthropics/claude-code/issues/25714)). Needs a
    `remaining_context − (est_results × n_agents) > margin` check before launching.
11. **Test bloat.** Models over-test every tiny change. See
    [Leg 3](#leg-3--lifetime) — and note that commit history is the audit trail.
12. **Savings counters treated as evidence.** `rtk` reported 99.8% savings while
    the bill rose. Only the bill counts.
13. **GraphRAG-global as the default answer to "we need better retrieval."**
    **331,375 average prompt tokens** against vector RAG's 879, and it scales with
    corpus size — 7,800 → 40,000 as query difficulty rises
    ([arXiv 2506.05690](https://arxiv.org/html/2506.05690v3)). The capability being
    added is answering dataset-wide questions. The cost is being paid on every
    query, including the 90% that are single-hop lookups vector RAG handles at
    879 tokens. Route by question type instead.
14. **LLM-written edges and community summaries at ingestion.** The expensive
    half of every graph pipeline. Extraction-free construction reaches comparable
    graph quality at **1,043× fewer indexing tokens**
    ([ContextRAG](https://arxiv.org/pdf/2605.19735)); LazyGraphRAG matches graph
    answer quality at **0.1% of the index cost**. If a join can produce the edge,
    an LLM shouldn't be writing it.
15. **Assuming you have a cache.** Authentication silently decides it. Gemini
    CLI gets context caching on API-key or Vertex auth and **none at all on
    OAuth**, because Code Assist can't create cached content. Same model, same
    prefix, same code — 10× the price. Check the provider's auth path before
    budgeting a single cached token.
16. **Long TTLs on caches nobody re-reads.** Gemini explicit caching bills
    storage **per hour per million tokens**. A generous TTL on a corpus that
    went stale is not a safety margin; it's a recurring bill for content you
    stopped reading. Re-read frequency, not caution, should set the TTL.
17. **Enabling deletion without watching the hit rate.** The reported wins are
    real (+29% performance, −84% tokens) and the reported cost is real
    (cache invalidation on every clear). Which one dominates *your* workload is
    unknowable without a hit-rate metric — see [Law 7](#laws).
18. **A deletion pass that doesn't persist its own state.**
    [`ClearToolUsesEdit`](https://github.com/langchain-ai/langchain/issues/37815)
    re-fires every turn against a checkpointer, re-clearing already-cleared
    results and paying for a fresh token count each time. Deletion bugs cost
    money in the direction people forget to check.

---

## Related

Adjacent lists, linked rather than duplicated:

- [Glossary](GLOSSARY.md) — every load-bearing term in this list, defined once with the number that makes it matter.
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers) — the catalogs. Check your schema cost before connecting one.
- [agentskills.io](https://agentskills.io/) · [spec](https://agentskills.io/specification) — three-tier progressive disclosure: ~100 tokens of catalog per skill, <5k instructions on activation, unlimited resources on access.
- [AGENTS.md](https://agents.md/) — nested-scoped instructions, 60k+ projects, stewarded by the Agentic AI Foundation under the Linux Foundation.
- [library-skills](https://github.com/tiangolo/library-skills) — libraries ship their own version-locked `SKILL.md`, symlinked into `.agents/skills`. **Freshness as a token strategy:** you cannot compress your way out of stale knowledge, and pay-for-what-you-import means skills for libraries you don't depend on cost zero.
- [llms.txt](https://llmstxt.org/) — the identifier-not-content pattern, generalized to the web.
- [Awesome Context Engineering](https://github.com/jihoo-kim/awesome-context-engineering) · [decispherhq](https://decispherhq.github.io/awesome-context-engineering) — broader and capability-shaped. Good neighbors; this list is budget-shaped.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version:

1. **Every entry gets an evidence grade.** `[measured]`, `[self-reported]`,
   `[asserted]`, or `[negative]`. An entry without one will be asked for one.
2. **`[measured]` needs a baseline and a method.** Model, harness, date, n, and
   a significance test where you have them. A number without a baseline is
   `[self-reported]`, however big.
3. **State which leg and which number moved.** `in` / `out` / `lifetime` /
   `⚡ serve-side`, plus `Δ tokens-in │ Δ tokens-out │ Δ $ / Δ wall-clock`.
4. **Every technique entry needs an additive clause.** "Keep the capability, drop
   the cost." If you can't write one, it belongs in [Anti-patterns](#anti-patterns).
5. **Negative results are the most valuable contributions here.** If you measured
   something that didn't work, that's a first-class entry.

---

## License

[CC0 1.0 Universal](LICENSE). Fork it, copy it, print it on a wall.
