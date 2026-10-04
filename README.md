# Awesome Token Minimalism

> **Minimal in, minimal out, minimal forever.**
> Papers, tools, and patterns for spending fewer tokens on all three sides of an LLM call.

A token is spent **once when you send it**, **once when you receive it**, and
**every day after** for everything you emitted. Most of the industry optimizes
the first. The bill for the third is the one nobody has instrumented.

---

## Contents

- [The three legs](#the-three-legs)
- [What counts as bloat](#what-counts-as-bloat)
- [Evidence grades](#evidence-grades)
- [Leg 0 — Measure](#leg-0--measure)
- [Leg 1 — Input](#leg-1--input)
- [Leg 2 — Output](#leg-2--output)
- [Leg 3 — Lifetime](#leg-3--lifetime)
- [Serve-side](#serve-side-cost-and-latency-not-token-count)
- [Interaction matrix](#interaction-matrix)
- [Laws](#laws)
- [Token ledger](#token-ledger)
- [Open problems](#open-problems)
- [Anti-patterns](#anti-patterns)
- [Contributing](#contributing)

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
diminishing returns**. Every model tested got measurably worse as input grew,
long before any stated limit.

- [Context rot (Chroma, 2025)](https://research.trychroma.com/context-rot) · `18 models, all degraded` · `[measured]`
  · [replication toolkit](https://github.com/chroma-core/context-rot)
- [RULER (NVIDIA)](https://github.com/NVIDIA/RULER) · `claimed 128K, effective 64K` · `[measured]`
- [Lost in the Middle (TACL 2024)](https://aclanthology.org/2024.tacl-1.9/) · `mid-context info → closed-book accuracy` · `[measured]`

### Output, in one line

Most of your output bill is invisible. **Reasoning tokens are billed at the
output rate** and are usually not broken out on any dashboard. A single call
with an 8,200-token thinking pass cost **7.2× more** than the same call without
it — with an identical visible response.

- [Brevity is the soul of sustainability (ACL 2025)](https://aclanthology.org/2025.findings-acl.1125/) · `−25…60% length, quality preserved` · `[measured]`
- [Token-Budget-Aware LLM Reasoning / TALE (ACL 2025)](https://aclanthology.org/2025.findings-acl.1274/) · `−67% output, GSM8K accuracy 81.35 → 84.46%` · `[measured]`

### Lifetime, in one line

Every line an agent generates is a permanent charge on every future session that
touches that subsystem. OpenClaw deleted **~400k LOC of its own tests** with
little change in coverage.

- [test-audit skill (OpenClaw)](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md) · `−400k LOC tests, coverage held` · `[self-reported]`
- [test-bloat patterns in commit history](https://git.mineracks.com/openclaw/openclaw/commits/commit/61dc7ac67994b8a8ae370d8d90200e87746d1b22) · `37 commits in one burst, "expand X coverage" ×12` · `[measured]`

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
marketing is `[asserted]`, and roughly a third of the *popular* ones fail
independent measurement. See the [ledger](#token-ledger).

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

### 📐 Budget

Allocate the window before you fill it. A cap set uniformly across heterogeneous
work is itself bloat.

- **[Anthropic: advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)** — explicit decision thresholds. Use Programmatic Tool Calling when tool definitions exceed 10k tokens, when tool-selection accuracy is a problem, or with 10+ tools. *Don't* when the library is under 10 tools, all are used every session, and schemas are compact. `[measured]`
- **[TALE (ACL 2025)](https://aclanthology.org/2025.findings-acl.1274/)** — the model estimates its own budget per problem, then reasons against it. `[measured]`
- **[ctxbudget CI gate](https://github.com/davidcjw/ctxbudget)** — `--fail-under 80` fails a build when context health drops. `[self-reported]`
- **[CLAUDE.md ≤ 3k tokens](https://github.com/JoeArmageddon/Claude-Master-Skill/blob/main/docs/token-budget.md)** — the 3,000-token / 40-instruction cap, and the finding behind it: adherence degrades past ~150–200 total instructions, *including the ones you care about*. Also: MCP server limit of 10. `[self-reported]`
- **[< 100 lines of CLAUDE.md](https://gist.github.com/yurukusa/556f67c493a2729ce9b1703f5003a227)** — 50–100 lines is the balance; 200+ means split into `.claude/rules/`. Plus allowlist-over-blocklist and move-safety-rules-to-hooks. `[self-reported]`

### 🔎 Select

Retrieval is a **runtime** decision, not a preprocessing step. Hold identifiers
(a file path, a query, a URL) and load the payload when the task needs it.

- **[Anthropic: effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — the canonical statement: *find the smallest possible set of high-signal tokens*. Attention budget, n² pairwise relationships, just-in-time retrieval, progressive disclosure, compaction, note-taking, subagents, tool-result clearing. `[measured]`
- **[Tool Search Tool](https://www.anthropic.com/engineering/advanced-tool-use)** — 134k → 8.7k tokens, **and** tool selection improved: Opus 4 49% → 74%, Opus 4.5 79.5% → 88.1%. Fewer schemas, better choices. `[self-reported]`
- **[MCP client best practices](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/docs/2026-07-28/develop/clients/client-best-practices.mdx)** — progressive discovery + programmatic tool calling, with the threshold at which to switch. `[measured]`
- **[RAG-MCP](https://arxiv.org/html/2505.03275v1)** — semantic retrieval over MCP schemas; retrieve top-k tool descriptions instead of all of them. `[measured]`
- **[SEP-1576: mitigating token bloat in MCP](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576)** — schema redundancy analysis, URL-addressed schemas, embedding-based tool retrieval. `[measured]`
- **[python-sdk #2619: context bloat is the MCP bottleneck](https://github.com/modelcontextprotocol/python-sdk/issues/2619)** — the structural case for grouping: no partial-loading primitive in the spec, so every workaround lives above the protocol. `[measured]`
- **[Serena](https://github.com/oraios/serena)** — symbol-level retrieval and editing over LSP. Ships `.serena/memories/` for cross-session orientation. ⚠️ See the negative result below. `[asserted]`
- **[serena-slim](https://github.com/mcpslim/serena-slim)** — 29 tools → 18, schema tokens 7,348 → 1,614 (−78%). Good example of tool consolidation as a token lever. `[self-reported]`
- **[SWE-grep (Cognition)](https://cognition.com/blog)** — RL-trained agentic retrieval for fast parallel context fetch, order of magnitude less time than frontier coding models. `[self-reported]`

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

### 💾 Cache

Cheapest input tokens are the ones you don't re-send.

- **[Anthropic: prompt caching](https://claude.com/blog/prompt-caching)** — write costs 1.25× base input, reads cost 0.1×. Up to −90% cost, −85% latency on long prompts. `[measured]`
- **[Don't Break the Cache](https://arxiv.org/html/2601.06007v1)** — across OpenAI/Anthropic/Google: 45–80% cost, 13–31% TTFT. Also the part everyone gets wrong: **what invalidates a prefix** (timestamps in the system prompt, tool-definition changes, mid-session model switches). `[measured]`
- **[CAPC: cache-aware prompt compression](https://arxiv.org/html/2607.15516v1)** — the first honest cost model of compress × cache interaction. `[measured]`

**Rules that matter more than the features:**
1. Stable content first (system prompt → tool definitions → history), variable last.
2. Keep the prefix byte-identical between turns. A request ID in the system prompt kills every subsequent hit.
3. Cache operates on ~1k-token blocks. A 300-token prompt has nothing to reuse.

### 🗑️ Delete (narrow)

The narrowest sense of the word: stop paying for a tool result you already read.

- **[Anthropic: tool result clearing](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — described as the safest, lightest touch. Clear after the turn in which it was consumed. `[measured]`
- **[Contextual Memory Virtualisation](https://github.com/CosmoNaught/claude-code-cmv)** — strip tool-result bodies, base64 blocks, and thinking signatures; keep every user and assistant message verbatim. 132k → 2.3k. Named snapshots, branching, trimming — version control for context. `[self-reported]`
- **[`/clear` vs `/compact`](https://github.com/jaczaar/claude-code-bestpractices/blob/master/research/02-context-management.md)** — `/compact` summarizes and keeps you in the same topic; `/clear` is a hard reset. Don't carry a database migration into a frontend feature. `[asserted]`
- **[contextwatch](https://pypi.org/project/contextwatch/)** — find the specific turn-3 tool result still costing 8k tokens at turn 20. `[self-reported]`

> ⚠️ **Deletion has a blast radius.** [microcompact cleared MCP-backed user
> memory](https://github.com/anthropics/claude-code/issues/57788) without notice
> or opt-in, and the model could not self-diagnose the loss. Deleting output that
> a downstream system treats as durable storage is not an optimization. **Verify
> the summary before you delete the source.** See
> [Leg 3 retention bars](#-%EF%B8%8F-retention-bars-dont-delete-without-one).

---

## Leg 2 — Output

### 📐 Audit

Start here. Most of the output bill is invisible.

- **[Thinking tokens are billed at the output rate](https://getnadir.com/blog/extended-thinking-tokens-output-billing)** — $25/M vs $5/M input on Opus-class. Worked example: 8,200 thinking tokens added **$0.205 to a $0.033 call — 7.2× total, identical visible response.** Most teams have never calculated reasoning overhead as a share of output spend. `[measured]`
- **[The hidden cost of "cheap" AI](https://dev.to/max_quimby/the-hidden-cost-of-cheap-ai-why-budget-reasoning-models-actually-cost-6x-more-3e0)** — thinking tokens are **>80% of total output cost**. Removing them from the analysis raises the price↔actual-cost correlation from 0.563 to 0.873 and eliminates 70% of rank reversals. Gemini 3 Flash burned 208M thinking tokens on GPQA. *This is the single most important table in the output half.* `[measured]`
- **[Brevity is the soul of sustainability (ACL 2025)](https://aclanthology.org/2025.findings-acl.1125/)** — the taxonomy everything else builds on: **MinAns** (minimal answer) vs **Irrel** (irrelevant, hallucinated, repeating). MINANS framing ≈ −60% output tokens, explicit length prediction −53%. Annotated dataset released. `[measured]`
- **[Verbosity Compensation Behavior (UncertaiNLP 2025)](https://aclanthology.org/2025.uncertainlp-main.14/)** — models trained toward brevity get *worse* at concise answers. Distilling Mistral→GPT cut verbosity compensation from 63.81%→31.79% down to 16.60%. **Brevity can be a training artifact, not a prompt property.** `[measured]`
- **[Computational Challenges in Token Economics](https://arxiv.org/pdf/2605.17410)** — treats tokens as economic primitives; frames the granularity / real-time / optimality tension. Good survey of the vocabulary. `[measured]`

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

### 📏 Constrain

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

> **You emit context, you don't just spend it.** Every line an agent generates is
> a charge on every future session that touches that subsystem. Review artifact
> cost the way you review API cost.

### 🗑️ Build less

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
[budget-inversion result](#%EF%B8%8F-budget), and they are the same law:

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

This is also the general form of the [microcompact failure](#%EF%B8%8F-delete-narrow):
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
| Shorter reasoning | ↔ Math accuracy | CCoT −27.69% on math (GPT-3.5); short reasoning hurt small and medium models too. Model- and task-dependent, not universal. |
| Tighter budgets | ↔ Budget compliance | 10-token budget → **157** output tokens, worse than a 50-token budget. Non-monotonic. |
| Enable thinking everywhere | ↔ Invisible bill | 7.2× cost, identical visible response, no dashboard line item. |
| Diff outputs | ↔ Edit robustness | find-replace is cheap but whitespace-brittle; whole-file rewrite is robust and expensive. [SWE-Edit](https://arxiv.org/html/2604.26102v1) learns to *choose per task* rather than pick a side. |
| Clear tool results | ↔ Durable memory | [microcompact](https://github.com/anthropics/claude-code/issues/57788) silently deleted user memory and the model could not self-diagnose. |
| Teach brevity via few-shot | ↔ Input cost | Exemplars load every call. caveman adds ~1–1.5k input tokens per turn for the skill itself — net-negative on already-terse work. |
| Fewer tools | ↔ Tool accuracy | Direction of effect is *contested*: Tool Search Tool reports selection improving 49% → 74%, but the [LSP measurement study](https://arxiv.org/pdf/2608.13568) found LSP tooling **costing** +6% (Opus) to +118% (Sonnet) on symbol-localization. Different mechanisms, both can be true. |
| **Prune the artifact** | ↔ **Future debug cost** | **Delete a guard that mattered → bug → more sessions → more lifetime context than you saved.** The lifetime axis has the *same* re-fetch trap as compression: **tokens-per-task, not tokens-per-edit.** |
| Bounded goal | ↔ Gaming | "−20% while holding coverage within 2%" is gameable both ways: pick the easy 20%, or delete only redundant tests and stop. Needs an independent guard metric. |

> **The last two rows are where this list argues with itself.** test-audit's own
> technique invites the failure the repo exists to catch. Flagged, not resolved.

---

## Laws

**Input**

1. Context is a budget, not a bucket. Spend it like money.
2. The cheapest token is the one you never send.
3. Identifiers beat payloads. A file path is ~12 tokens; the file is 4,000.
4. Every tool schema is a permanent tax on every turn.
5. Compress and cache are antagonistic. Pick a regime deliberately.
6. Advertised context ≠ effective context. Benchmark yours.

**Output**

7. Output tokens are 5× the price. Treat them as the scarce resource.
8. **Reasoning tokens are output tokens. Instrument them, or they're free money for your provider.**
9. A budget you can't meet isn't a budget — it's a suggestion the model overpays on.
10. Prefer a schema to a paragraph; a tool call to a sentence.
11. Ask for the smallest thing that answers the question. Then check that it did.
12. A diff is not a rewrite. Edit protocols are a token decision.
13. Verbosity is trainable, which means brevity is sometimes an artifact, not a fact. Measure per model.
14. Token count, latency, and dollars are three different numbers. Know which one you reduced.

**Lifetime**

15. **You emit context, you don't just spend it.** Review artifact cost like API cost.
16. **An open-ended cleanup goal will be undershot. Bound it** — name the target and the guard metric.
17. **A deletion without a retention bar is a regression with extra steps.** State what each thing independently protects before removing it.
18. **Never convert uncertain candidates into cleanup to hit a number.** This applies to PRs and to ledger entries alike.
19. Optimize tokens-per-**task**, not tokens-per-request or per-edit. Re-fetching is the hidden cost on all three legs.

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

---

## Related

Adjacent lists, linked rather than duplicated:

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
