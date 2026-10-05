# Token Maxxing

> **The other direction.** A token has three clocks; tokenmaxxing is what
> happens when nobody reads the meter. This is the catalog of blow-ups — the
> negative results, kept on purpose, because the pattern is easier to recognize
> on someone else's bill than on your own.

Part of [Awesome Token Minimalism](README.md).

---

## The scoreboard

The worst measured numbers in this catalog, in one place. Every figure is
graded and linked below.

| Case | The number | Source |
|---|---|---|
| One MCP tool, average output | **557,766 tokens** | [MSR](https://www.microsoft.com/en-us/research/blog/tool-space-interference-in-the-mcp-era-designing-for-agent-compatibility-at-scale) |
| GraphRAG-global, per query | **331,375 tokens** vs vector RAG's **879** | [arXiv 2506.05690](https://arxiv.org/html/2506.05690v3) |
| A $0.033 call with thinking on | **+$0.205 (7.2×)** | [Nadir](https://getnadir.com/blog/extended-thinking-tokens-output-billing) |
| Screenshot vs ARIA snapshot | **15,704 vs 121 tokens (129.8×)** | [caveman](https://github.com/JuliusBrussee/caveman) |
| Thinking tokens on GPQA (Gemini 3 Flash) | **208M tokens** | [dev.to](https://dev.to/max_quimby/the-hidden-cost-of-cheap-ai-why-budget-reasoning-models-actually-cost-6x-more-3e0) |
| 14 background agents | **~1.1M tokens, zero usable output** | [claude-code #25714](https://github.com/anthropics/claude-code/issues/25714) |

---

## What it is

**Tokenmaxxing is spending tokens as the objective, not the cost.** It is not
"using a lot of tokens" — a long, measured context is fine. It is the moment the
count becomes a scoreboard: more context, more agents, more thinking, more
samples, and the outcome is never priced against the spend.

The test is the list's definition of [bloat](README.md#what-counts-as-bloat):

> Bloat is any token whose cost has not been measured against its contribution.

Tokenmaxxing is bloat that got a budget line and a leaderboard.

**The measuring stick is tokens-per-task, not tokens-per-request.** Every case
below is an instance of the same error: a number went up, and nobody asked what
it bought. Grades mean what they mean in the list — `[measured]`,
`[self-reported]`, `[asserted]`, `[negative]` — see
[Evidence grades](README.md#evidence-grades).

---

## 1. Fleet scale: the bill with no ceiling

- **[The token bill comes due (TechCrunch)](https://techcrunch.com/2026/06/05/the-token-bill-comes-due-inside-the-industry-scramble-to-manage-ais-runaway-costs/)** — Uber exhausted its annual Claude Code budget in four months; the FinOps Foundation reported companies **3× over their 2026 token budget by April**. Per-token prices were *falling* while total bills rose. `[asserted]`
- **[Uber's COO on AI token spend (Business Insider)](https://www.businessinsider.com/uber-coo-andrew-macdonald-ai-token-spending-harder-justify-2026-5)** — no demonstrable link between token spend and shipped features. The demand-side reason tokenmaxxing ended. `[asserted]`
- **[Is "tokenmaxxing" cost effective? (Jellyfish)](https://jellyfish.co/blog/is-tokenmaxxing-cost-effective-new-data-from-jellyfish-explains)** — the top 10% of Claude Code users spend roughly **10× the tokens for ~2× the output**; 275k+ engineers, baseline unstated. The diminishing-returns curve is the finding. `[self-reported]`
- **[AI acceleration whiplash (Faros AI)](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)** — a two-year study of 20,000 developers: output rose, and so did bugs and rewrites. `[self-reported]`
- **[Where's Your Ed At (Ed Zitron)](https://www.wheresyoured.at)** — seven-figure single-quarter token bills and per-seat caps appearing within months of the billing shift (reported Uber $1,500/month, T-Mobile $2,000/month, Brex $500/week for engineers). Polemical; cited for the demand-side figures. `[asserted]`
- **[From tokenmaxxing to token minimalism (Beyond Runtime)](https://beyondruntime.substack.com/p/from-tokenmaxxing-to-token-minimalism)** — the cultural shift, Uber's blowout, and Goodhart's Law applied to token counts. `[asserted]`

## 2. The invisible line items

- **[Thinking tokens are billed at the output rate](https://getnadir.com/blog/extended-thinking-tokens-output-billing)** — 8,200 thinking tokens added **$0.205 to a $0.033 call — 7.2× the total**, for an identical visible response. `[measured]`
- **[The hidden cost of "cheap" AI](https://dev.to/max_quimby/the-hidden-cost-of-cheap-ai-why-budget-reasoning-models-actually-cost-6x-more-3e0)** — thinking tokens are **>80% of total output cost**; excluding them raises the price↔cost correlation from 0.563 to 0.873. Gemini 3 Flash burned **208M thinking tokens on GPQA**. `[measured]`
- **[Energy use of AI inference (Joule / Microsoft Research)](https://www.cell.com/joule/fulltext/S2542-4351%2826%2900114-5)** — frontier inference is a median **0.31 Wh/query**; a reasoning query at ~5,000 output tokens costs **~13×** that. Public estimates *overstate* energy by **4–20×**, so the real bill is both hidden and misquoted. `[measured]`
- **[The Energy Cost of Reasoning](https://arxiv.org/pdf/2505.14733v2)** — reasoning traces average **7,845 output tokens/query** and a ~258MB KV cache even at 7B. The inversion: a 7B *base* model buys **+16.8% accuracy for −40.1% energy**, while bolting reasoning onto a 1.5B buys **+17.3% accuracy for +57.4% energy** — same accuracy, opposite energy sign. `[measured]`
- **[How Hungry is AI?](https://arxiv.org/html/2505.09598v6)** — per-query energy, water, and carbon across models; a short session can draw **~0.5 L** of cooling water. `[measured]`

## 3. The tool-schema tax

- **[MCP compression at Atlassian](https://www.atlassian.com/blog/developer/mcp-compression-preventing-tool-bloat-in-ai-agents)** — GitHub MCP shipped **91 tools, ~17.6k tokens/session**, a flat payload injected on every turn. `[asserted]`
- **[Tool-space interference in the MCP era (MSR)](https://www.microsoft.com/en-us/research/blog/tool-space-interference-in-the-mcp-era-designing-for-agent-compatibility-at-scale)** — the worst single MCP tool averaged **557,766 output tokens**; **16 tools exceed 128k**. Bloat isn't incidental to the error — it *is* the error. `[measured]`
- **[Claude Code `/context` breakdown](https://github.com/Beaulewis1977/claude-code-context-command)** — one real setup: MCP schemas at **135.6k tokens, 76.6% of the window**, before the user types a character. `[self-reported]`
- **[Anthropic: advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)** — the countermeasure: Tool Search cut **134k → 8.7k tokens** and *raised* selection accuracy (Opus 4: 49% → 74%). Fewer schemas, better choices. `[self-reported]`

## 4. Retries, loops, and unbounded agents

- **[Unbounded background agents (claude-code #25714)](https://github.com/anthropics/claude-code/issues/25714)** — **14 agents × ~80k tokens, zero usable output**. Needs a `remaining_context − (est_results × n_agents) > margin` check before launch. `[asserted]`
- **[Loop length dominates agentic RAG (ACL 2026)](https://aclanthology.org/2026.gem-main.40)** — a 5-call session burns ~**250k tokens** against **36k** for 3 calls, *regardless of documents retrieved*. Optimizing the retriever while the loop grows is optimizing the small term. `[measured]`
- **[Unrouted vector-only retrieval (Forbes)](https://www.forbes.com/councils/forbestechcouncil/2026/07/09/rag-didnt-die-it-moved-up-the-stack)** — stuffing pays ~**1,000×** for degraded recall when retrieval should have moved up the stack. `[asserted]`

## 5. Graph and retrieval over-build

- **[When to use Graphs in RAG](https://arxiv.org/html/2506.05690v3)** — GraphRAG-global averaged **331,375 prompt tokens** against vector RAG's **879** on the same corpus, and scaled **7,800 → 40,000** as query difficulty rose. The cost moved from the query to the index. `[measured]`
- **[ContextRAG](https://arxiv.org/pdf/2605.19735)** — a HiRAG reproduction spent **870 calls / 3.54M tokens** on a 20-task subset and failed mid-construction; extraction-free construction did it in **30 calls / 22,073 tokens — 1,043× fewer**. Graph structure ≠ LLM summarization. `[measured]`
- **[LazyGraphRAG (Microsoft Research)](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost)** — the countermeasure: graph answer quality at **0.1% of full GraphRAG's index cost**. `[measured]`

## 6. Optimizers that cost more

- **[JetBrains: auditing token-saving skills](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested)** — the paired A/B that exposed the gap: `rtk` measured **+7.6% cost** at low effort against a −60…90% claim; `caveman` **−8.5%** against −65%; `ponytail` **−15.4% code / −10.3% cost** against −54%/−20%. Three tools, one harness, two failed to deliver. `[measured]`
- **[`rtk`](https://github.com/ai-skynet-labs/reduce-tokens)** — its own dashboard reported **96.2M tokens saved, 99.8% of everything it touched**, while the measured bill went **up**. A savings counter is not evidence; only the bill is. `[negative]`
- **[`caveman`](https://github.com/JuliusBrussee/caveman)** — advertised −65% output tokens; independently measured **−8.5%** (86 tasks, sign test p=0.82). `[measured]/[asserted]` — audit measured, headline not.
- **[`ponytail` vs `caveman` (curviate)](https://curviate.com/blog/ponytail-vs-caveman)** — on the rebuilt benchmark the free seven-word prompt *"Follow YAGNI, prefer one-liners"* matched the best tool on cost and time — and was the only arm to write an unsafe function (**95%** safe vs 100%). The cheapest intervention is not always the safest. `[measured]`
- **[`token-saviour`](https://github.com/vagkaratzas/token-saviour)** — claims −69.6% stacked, directly contradicting the JetBrains `rtk` result (+7.6%). Different harness, different cost basis: contested. `[self-reported]`
- **[langchain #37815](https://github.com/langchain-ai/langchain/issues/37815)** — `ClearToolUsesEdit` **fires every turn** with a checkpointer, re-clearing already-cleared results and paying for a fresh token count each time. A deletion feature that silently costs money. `[negative]`
- **[microcompact (claude-code #57788)](https://github.com/anthropics/claude-code/issues/57788)** — server-side deletion **silently cleared MCP-backed user memory**, with no notice and no opt-in, and the model could not self-diagnose the loss. `[negative]`

## 7. Multimodal overpay

- **[Browser automation: snapshot vs screenshot](https://github.com/JuliusBrussee/caveman)** — a focused question against a 200-row table: **121 tokens** as a Playwright ARIA snapshot vs **15,704** as a screenshot — **129.8×**. Honest caveat: on tiny forms the snapshot *loses* 2.3×. `[self-reported]`
- **[OpenAI image input cost](https://developers.openai.com/api/docs/guides/image-cost-calculator)** — `gpt-4o-mini` is **2,833 + 5,667 per tile** — **33× the tile cost of its sibling** for the same image. `[measured]`
- **[`detail: low`](https://platform.openai.com/docs/guides/images-vision)** — flat 85 tokens; full resolution is a **30× overpay** when you only need to know what the image is (2,805 vs 85). `[measured]`
- **[Gemini video and audio rates](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/embeddings/get-multimodal-embeddings)** — video at **263 tokens/second**: a one-minute clip is **~15,780 tokens**, a full context window before any question is asked. `[measured]`

## 8. A generative model for a bounded decision

- **[Jev, independently benchmarked](https://arxiv.org/abs/2609.37647)** — **346,009 classification requests for under US$10** against two open models on identical requests. The same work routed through a generative LLM is a different order of magnitude. `[measured]`
- **[Introducing System One models (TypeSafe AI)](https://typesafe.ai/blog/introducing-system-one-models-and-jev)** — `choice` (one of ≤255), `score` (a rubric), and `noul` (a yes/no probability) return typed values in one forward pass; output is priced at **$0.00** because no text is generated. `[self-reported]`

## 9. The meter nobody reads: joules and water

- **[Key Questions on Energy and AI (IEA)](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary)** — data centres consumed **~485 TWh in 2025**, projected **~950 TWh by 2030**; consumption from AI-focused data centres grew **50% in 2025** alone. `[measured]`
- **[How Hungry is AI?](https://arxiv.org/html/2505.09598v6)** — the per-query water and energy accounting that makes token spend an environmental line item, not only a dollar one. `[measured]`

---

## The pattern

Six moves produce almost every case above, and each has a countermeasure in the
list:

1. **Per-request, not per-task.** The metric rewards shrinking one call and
   ignores the re-fetching it causes. → [tokens-per-task](README.md#laws)
2. **Defaults, not decisions.** Nobody chose 91 tool schemas or 8,200 thinking
   tokens; a default shipped unmeasured. → [Anti-patterns](README.md#anti-patterns)
3. **Uniform configuration.** Thinking on 100% of calls, one budget for every
   task, the same model for every branch. → [Interaction matrix](README.md#interaction-matrix)
4. **Counters, not the bill.** The tool's own dashboard reported 99.8% savings
   while the cost rose. → [Token ledger](README.md#token-ledger)
5. **Retrieval volume, not loop length.** Sequential tool calls dominate the
   bill; document count is the small term. → [Graph engineering](README.md#%F0%9F%95%B8%EF%B8%8F-graph-engineering)
6. **Capability, never measured.** A capability is not bloat; a capability whose
   cost was never priced is. → [What counts as bloat](README.md#what-counts-as-bloat)

> **The exit is a receipt.** Every case here is a number that went up with no
> baseline attached. The fix is never "use fewer tokens" as a slogan — it is the
> same move the rest of the list makes: name the capability, keep it, and remove
> the cost you can finally see.

---

## See also

- [Token ledger](README.md#token-ledger) — advertised vs. independently measured
- [Anti-patterns](README.md#anti-patterns) — the defaults that produced these bills
- [Open problems](README.md#open-problems) — what nobody has measured yet
- [Resources](RESOURCES.md) — the primary sources behind the catalog
