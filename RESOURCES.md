# Resources

External reading that shapes the list's positions — standards, industry context,
primary-source talks, and practitioner playbooks. These are **not** entries in
the [awesome list](README.md): if it is something you install, run, or measure,
it belongs in the README. If it is something you read to understand *why* the
list takes the position it does, it belongs here.

Part of [Awesome Token Minimalism](README.md).

---

## Frameworks & consultancies

Organizations packaging the idea into a practice. Consultancy-shaped — the
framework is the deliverable, so grade the numbers accordingly.

- **[Token Minimalism Framework (QConsul)](https://qconsultai.com/token-minimalism)** — treats compute as a finite resource to steward on behalf of people, planet, and profit. Fleet-scale token management: 14 agents, 115 skills, ~174k tokens total. Grades token spend as a budget line item and safety concern for autonomous AI. `[self-reported]`

## Standards & governance

The institutional layer: bodies defining how token spend gets measured,
attributed, and standardized. The list's Leg 0 says *measure first*; these are
the people writing the schema your dashboard will measure in.

- **[Tokenomics Foundation (Linux Foundation)](https://www.linuxfoundation.org/press/linux-foundation-launches-the-tokenomics-foundation-to-define-the-economics-and-roi-of-ai-value)** — vendor-neutral standards body launched Aug 2026 with ~30 founding members, in partnership with the FinOps Foundation. Scope: shared language, benchmarks, and total-cost-of-ownership models for token production, consumption, and monetization. The signal that token cost is becoming an institution-level discipline rather than a vendor feature. `[asserted]`
- **[FinOps Foundation — Tokenomics: Managing AI Value in SaaS Model Token Costs](https://www.finops.org/wg/token-economics-saas)** — names the structural causes of token-cost opacity: developer-led purchasing, opaque billing, no native allocation mechanism, and pricing that varies across model tiers. The community-standard attempt to fix them. `[self-reported]`
- **[FinOps Foundation — FinOps for AI Overview](https://www.finops.org/wg/finops-for-ai-overview)** — the framework counterpart to this list's measurement leg: cost-per-token as a first-class metric, quotas, tagging, and caching as an optimization. Useful for translating a token bill into a governance model. `[self-reported]`
- **[FOCUS specification](https://focus.finops.org)** — open billing-data schema for cloud spend, now being extended to token-based billing. The format a FinOps dashboard reads tokens in. `[asserted]`

## Books

Longer-form treatments of the same trade-offs. Where a README section is a
receipt, a book is the argument behind it — slower to date, but durable.

- **[AI Engineering (Chip Huyen, O'Reilly 2025)](https://huyenchip.com/books)** — the inference-optimization chapter is the book-length version of Leg 2: time-to-first-token versus time-per-output-token, quantization, distillation, prompt caching, batching, and the "climb only as high as you must" ladder from prompting to fine-tuning. Frames latency and cost as the bottleneck that decides whether a model is usable at all. `[asserted]`

## Essays & analysis

Argument-shaped writing: the *why* rather than the *how much*. Useful for
framing, not for numbers.

- **[From tokenmaxxing to token minimalism (Beyond Runtime)](https://beyondruntime.substack.com/p/from-tokenmaxxing-to-token-minimalism)** — the shift from competing on token consumption to treating tokens as a resource to use precisely. Covers Uber's budget blowout, Goodhart's Law, and the cultural shift toward minimalism. `[asserted]`
- **[The Token Tax: Why GenAI Billing Makes Minimalist Architecture Mandatory (dev.to)](https://dev.to/dmitryame/the-token-tax-why-genai-billing-makes-minimalist-architecture-mandatory-4fl2)** — argues that token-based billing makes every architectural decision a cost decision. Fragmented stacks force larger context windows and cross-language reasoning; minimal stacks enable small, language-specialized models. `[asserted]`

## Critical & skeptical takes

The demand-side counter-argument: that AI spend may not have an ROI to optimize
in the first place. Included because negative results are first-class here, and
because a case for minimalism is stronger when it survives the strongest
objection. Read the numbers, not the register.

- **[Where's Your Ed At (Ed Zitron)](https://www.wheresyoured.at)** — the most sustained public case that enterprise AI spend is not paying off: token-based billing reaching enterprises only in 2026, seven-figure single-quarter token bills, and per-seat caps appearing within months of the shift (reportedly Uber at $1,500/month, T-Mobile at $2,000/month, Brex at $500/week for engineers). Polemical; cited for the demand-side figures. `[asserted]`
- **[Zitron Dumbtron — a scored audit of Ed Zitron on AI](https://zitron.nickwarino.com)** — an independent, claim-by-claim audit with a published scoring method that grades his right/wrong rate *by topic* rather than by volume. This repo's own move — grade each claim — applied to a professional critic. Pair it with the entry above so the reader sees both the argument and its calibration. `[self-reported]`

## Practitioner playbooks

Frameworks for deciding what earns a place in the window. Practitioner-shaped
rather than vendor-measured — grade them as organizing vocabulary, not evidence.

- **[LangChain — Context engineering for agents](https://blog.langchain.com/context-engineering-for-agents/)** — the **Write / Select / Compress / Isolate** taxonomy: the four levers on an agent's context, mapped to where each applies. The clearest checklist form of the Input leg's argument. `[asserted]`
- **[Sourcegraph — Context Engineering: A Practical Guide for AI Agents (2026)](https://sourcegraph.com/blog/context-engineering)** — production framing of token-budget management as cutting low-signal content *before* it enters the window, not after: truncate tool output, compact resolved turns, drop below a relevance threshold, cap retrieval candidates. `[asserted]`

## Prices, tokens & model references

The lookup layer. The README's [break-even](README.md#%F0%9F%A7%AE-break-even)
inequalities are only as good as the prices and token counts you feed them, and
both move with every release. These are the references to re-derive the
constants from — not savings claims.

- **[llm-prices.com (Simon Willison)](https://llm-prices.com)** — live input/output/cached price table across providers, maintained through price changes and model retirements. The source of truth for re-deriving `r` (output ÷ input) and the cache read/write ratios the break-even section says to re-check. `[self-reported]`
- **[Artificial Analysis](https://artificialanalysis.ai)** — independent intelligence, latency, and price leaderboards alongside provider benchmarks. The data behind the "right model for the task" trade, including the per-token prices that make a small decision model economic. `[self-reported]`
- **[Anthropic — token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)** — `messages.count_tokens` on the same message array you will send, including system prompt and tool definitions. Returns the count that matches billing, which is what the [three-number convention](CONTRIBUTING.md#the-three-numbers-not-one) depends on. `[self-reported]`
- **[tiktoken (OpenAI)](https://github.com/openai/tiktoken)** — the open BPE tokenizer. Exact for OpenAI models; the widely used fallback estimate for providers that do not publish a tokenizer. `[self-reported]`
- **[Gemini — token counting and usage](https://ai.google.dev/gemini-api/docs/tokens)** — `count_tokens` before sending; the response `usage` splits input, output, **thinking**, cached, and tool-use tokens. The thinking split is the line most dashboards omit, and the one [Leg 2 · Audit](README.md#%F0%9F%93%90-audit) says to instrument. `[self-reported]`
- **[OpenRouter model catalog](https://openrouter.ai/models)** — one key across providers at pass-through pricing. Useful for the routing levers — a small model for the easy branch, a frontier model for the hard one — without separate billing per provider. `[self-reported]`

## Benchmarks & evaluation corpora

The datasets behind the list's accuracy claims, so a reader can reproduce them
rather than trust them. The closest thing here to measurement equipment — but
still third-party harnesses, not this repo's.

- **[LongMemEval](https://github.com/xiaowu0162/LongMemEval)** — 500 curated questions across five abilities: extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention. The focused-versus-full arm is the cleanest evidence for [relevance density](README.md#the-accuracy-gain) in the list; linking the corpus lets you re-run it. `[self-reported]`
- **[mem0 — AI memory benchmarks in 2026](https://mem0.ai/library/agent-memory/ai-memory-benchmarks-in-2026)** — an index of LongMemEval, LoCoMo, and BEAM with dataset sizes (LongMemEval_S carries ~115k-token histories; _M stretches to ~500 sessions) and an explicit warning about leaderboard saturation. Vendor-published, useful as a map. `[self-reported]`
- **[Artificial Analysis — long-context reasoning eval](https://artificialanalysis.ai/evaluations/artificial-analysis-long-context-reasoning)** — 10k–100k-token extraction, reasoning, and synthesis tasks, tokenized with `cl100k_base`. The private-eval companion to [RULER](README.md#%F0%9F%93%8F-effective-context): where RULER finds the effective length, this tracks the current generation against it. `[self-reported]`

## Primary-source talks & podcasts

Where the vocabulary comes from, in the words of the people who built the tools.
Primary sources for quotes that circulate without them.

- **[Boris Cherny & Cat Wu — Reflecting on a year of Claude Code](https://www.youtube.com/watch?v=Hth_tLaC2j8)** — the origin of the phrase **"context minimalism."** The strongest form of the argument: *"give it the minimal possible system prompt, the minimal possible tools, and then let the model figure it out."* Also the maintenance claim under Leg 3: with every model release, they delete system-prompt and tool content. `[asserted]`
- **[Every / AI & I — How to Use Claude Code Like the People Who Built It](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it)** — companion interview with Cherny and Wu; transcript available. Primary source for the workflow behind the tool, including the subagent and context-management habits. `[asserted]`
- **[The Pragmatic Engineer — How Claude Code is built](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built)** — engineering-history deep dive with Cherny, Bidasaria, and Wu. Useful for seeing which early context decisions were later reversed, and why. `[asserted]`
- **[Y Combinator — Boris Cherny: Building Claude Code](https://www.ycombinator.com/library/UN-boris-cherny-building-claude-code)** — Startup School 2026 talk. Carries the harness-as-living-artifact claim: *"always adding stuff, always deleting stuff"* as the model changes. The strongest maintenance argument for keeping a system prompt small. `[asserted]`

## News & the token-bill reckoning

The demand-side context: why "use fewer tokens" moved from philosophy to
survival. Snapshot material — each item is stamped by its moment, and a
"3× over budget" anecdote is evidence of a period, not a law.

- **[TechCrunch — The token bill comes due](https://techcrunch.com/2026/06/05/the-token-bill-comes-due-inside-the-industry-scramble-to-manage-ais-runaway-costs/)** — the origin piece: Uber exhausts its annual Claude Code budget in four months, the FinOps Foundation reports companies 3× over their 2026 token budget by April, and Datadog/New Relic bolt on token-level observability. The framing that matters: per-token prices were *falling* while total bills rose. `[asserted]`
- **[Business Insider — Uber's COO on AI token spend](https://www.businessinsider.com/uber-coo-andrew-macdonald-ai-token-spending-harder-justify-2026-5)** — Andrew Macdonald on finding no demonstrable link between token spend and shipped features. The demand-side reason tokenmaxxing ended. `[asserted]`
- **[Faros AI — AI acceleration whiplash](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)** — a two-year study of 20,000 developers: output rose, and so did bugs and rewrites. Vendor-published, baseline unstated. `[self-reported]`
- **[Jellyfish — Is "tokenmaxxing" cost effective?](https://jellyfish.co/blog/is-tokenmaxxing-cost-effective-new-data-from-jellyfish-explains)** — the top 10% of Claude Code users spend roughly **10× the tokens for ~2× the output**. Vendor-published from a very large dataset (275k+ engineers), baseline unstated; the diminishing-returns curve is the useful part, not the absolute numbers. `[self-reported]`

## Newsletters & people to follow

The upkeep layer. Everything above decays — prices move weekly, context windows
change quarterly — and these are the places that track it as it happens.

- **[Simon Willison's Weblog](https://simonwillison.net)** — continuous, hands-on notes on model releases, pricing, and long-context behavior, usually within hours. His `llm-pricing` tag is effectively the changelog behind [llm-prices.com](https://llm-prices.com). `[self-reported]`
- **[Latent Space](https://www.latent.space)** — AI-engineer podcast and newsletter. Covers context engineering, agent-harness design, and cost-relevant releases and benchmarks as they land. `[asserted]`

---

## How to read this doc

- **Grades mean what they mean in the list.** `[measured]`, `[self-reported]`,
  `[asserted]`, `[negative]` — see [Evidence grades](README.md#evidence-grades).
  Nothing here is `[measured]` against this repo's own harness; it is reading
  material, and the grade says how much weight the source can bear.
- **Reference entries are lookup aids, not claims.** The price, tokenizer, and
  benchmark sections carry grades for source trustworthiness, not for any
  savings they assert. Re-derive the constants; do not quote them as results.
- **Link the primary source, not the listicle.** "10 Best LLM Observability
  Tools" roundups are marketing-shaped and are deliberately absent. If a source's
  only claim is a ranking, it does not belong here.
- **Vendor studies stay `[self-reported]` however large.** Faros and Jellyfish
  have real datasets; neither states a baseline a reader could re-run.
- **News decays.** Industry-coverage entries carry their month in the
  description. Treat them as snapshots of a moment, not standing facts.
