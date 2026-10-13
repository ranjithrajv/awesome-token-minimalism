# Contributing

Thanks for considering a contribution. This list has one editorial rule that
matters more than any other, and this file is mostly about it.

## Two ways in

| You're… | Open a PR against |
|---|---|
| A user, researcher, or bystander reporting what you measured | [`README.md`](README.md) — the list proper |
| **The maintainer of a tool** that belongs here | [`SHOWCASE.md`](SHOWCASE.md) — self-submitted, grade yours to state |

The showcase exists because the tools that most need listing are often ones nobody
has heard of, and the tools everyone lists are the ones that already have a
marketing budget. A maintainer knows the honest caveat nobody else would write down.

**The distinction is structural, not editorial.** The main list is assembled by
readers who didn't build the tool; the showcase is assembled by the authors.
`SHOWCASE.md` says so in its header, uses the same grade vocabulary below, and
never presents `[self-reported]` as `[measured]`. If you measure your own tool
properly — baseline stated, method re-runnable, n and a significance test where
you have them — put `[measured]` on the first line and expect the methodology
reviewed like anyone else's. That's the route into the main list.

Maintainers with a number but no harness: **[`harness/docs/submit-a-run.md`](harness/docs/submit-a-run.md)**
is the runbook — what a reviewer checks, how to run the rig this repo ships, and
what happens to the entry afterwards. There is also a
[submission form](.github/ISSUE_TEMPLATE/showcase-submission.yml) for the
structured start.

## The rule

**Every entry carries an evidence grade.**

| Grade | Means |
|---|---|
| `[measured]` | a number with a stated baseline and a method someone could re-run |
| `[self-reported]` | a number from the tool's own authors, baseline or harness unstated |
| `[asserted]` | a claim with no number — the default for anything marketing-shaped |
| `[negative]` | measured, and it did **not** work |

This is not bureaucracy. The gap between advertised and measured savings is
currently the least-measured quantity in the field: of three popular token tools
put through one paired A/B harness, one was `−8.5%` against a `−65%` claim, one
was **more expensive** than baseline, and one underdelivered on code size but
did deliver on cost. Nobody knew in advance. That is why the grades exist.

An entry submitted without a grade will get one, or a request for one.

## What a good entry looks like

```markdown
- **[tool-name](url)** — one line on what it does and which mechanism it uses.
  `Δin −85%` `Δout −98%` `Δ$ −60%` — baseline: naive stuffing, 2M-token docs.
  `[measured]` — claude-sonnet-5, Claude Code 2.1.201, 2026-07, n=80, p=0.004.
```

Five things, in this order:

1. **Name, linked.** One line on the mechanism — *what it actually does*, not
   what it's marketed as. "Wraps tool schemas and expands on demand" beats
   "powerful AI toolkit."
2. **Which leg and which number moved.** `in` / `out` / `lifetime` /
   `⚡ serve-side`, and then the three deltas: tokens in, tokens out, dollars or
   wall-clock. See below on why there are three.
3. **The baseline.** What were you comparing against? "Feels faster" is not a
   baseline. "vs. loading all schemas on connect" is.
4. **The grade.**
5. **The stamp, if you have one.** Model, harness, date, n, significance test.
   Optional — `[measured]` does not require a lab — but a `[measured]` without a
   stated baseline is really `[self-reported]`, and we will relabel it.
6. **Who measured it**, if you are submitting to the [token
   ledger](README.md#token-ledger). A ledger row is `[measured]` only when a
   party other than the tool's own author ran it. An author-published number with
   a harness and a baseline is better evidence than a bare claim, but it is still
   `[self-reported]` — say so in the `Measured by` column rather than letting the
   reader assume.

## The three numbers, not one

Token count, dollars, and wall-clock are different quantities and tools move
different ones.

Speculative decoding is the clean example: it is **lossless** — identical output
distribution — and cuts cost per token ~60% and latency 2–3×. **It reduces zero
tokens.** If your entry only moves cost or latency, mark it `⚡ serve-side`
rather than claiming a token reduction.

**Energy is the third gain and it is deliberately not a fourth number.**
Inference energy tracks output length and KV work, both of which are token
quantities, so a token delta *is* an energy delta and repeating it would be
noise. Break the convention only where the relationship is surprising — a
reasoning query running **~13×** the energy of a standard one, or a KV-cache hit
skipping joules as well as dollars.

Similarly, note *when* a saving lands. Prompt compression shows up as input
tokens today and latency on the next turn. Caching shows up as cost on turn 2+.
`rtk` reported 99.8% savings on a counter while the bill went up, which is only
possible if nobody checked which number they were optimizing.

## Placement

| Section | Entry belongs there if it… |
|---|---|
| **Leg 0 — Measure** | makes an existing token cost visible |
| **Leg 1 — Input** | reduces what goes *into* the request |
| **Leg 2 — Output** | reduces what comes *out*, or reasoning tokens |
| **Leg 3 — Lifetime** | reduces what you emit that future sessions pay for |
| **⚡ Serve-side** | only moves `$` or latency, not tokens |
| **Anti-patterns** | is a *default that shipped unmeasured* |
| **Token ledger** | has been independently measured against its claim, by someone other than the author |

If you can't place an entry, that's usually a sign it hasn't been measured yet.
Say so in the PR and we'll figure out where it goes together.

## The additive clause

**Every technique entry needs an additive clause.** The list's position is that
capability and minimalism are not opposed: the capability is preserved and the
unmeasured cost is removed.

- ✅ "Keep all 91 tools. Route them on demand: 134k → 8.7k tokens, and tool
  selection *improves* 49% → 74%."
- ✅ "Keep whole-file rewrite for restructuring. Select the format per task:
  −17.9% cost *and* edit success 93.4% → 96.9%."
- ❌ "Don't connect so many MCP servers."
- ❌ "Stop using chain-of-thought."

If you can't write the additive clause, the entry is either `[asserted]` or it
belongs in [Anti-patterns](ANTI-PATTERNS.md). Both are fine outcomes. The
failure mode we're guarding against is a technique post that reads like "you have
too much stuff" — that's the tone that gets lists like this dismissed as
cost-saving blogs, and it's why every entry here needs a number.

## Negative results are the most valuable thing you can add

If you measured something that didn't work — or that worked but cost more, or
worked only at one model or one harness — **that is a first-class contribution.**
Grade it `[negative]`, put the methodology in the entry, and say what would make
it work.

Two examples already in the list:

- An LSP-based navigation tool advertised as token-efficient was measured **costing**
  +6% (Opus) to +118% (Sonnet) tokens on symbol-localization — and the paper's
  own framing is the best line in this repo: *"the token-efficiency of semantic
  retrieval is asserted, not measured."*
- A 400k-LOC test deletion is a genuinely impressive result reported with **no n,
  no harness, no baseline, and coverage as the only guard metric.** We list it as
  `[self-reported]` and say why, because coverage is exactly the metric that can
  be gamed.

Neither of those entries is an attack on the tool's authors. Both are statements
about a number. That is the register.

## Open problems

The list has a standing [Open problems](OPEN-PROBLEMS.md) section with
sixteen questions nobody has answered. If you can answer one — even partially — that
outranks any number you could add to an existing section. Two worth calling out:

- **Where does a retention bar stop being worth its tokens?** It's prose in a
  skill: it costs tokens on every run and slows every deletion. Clearly worth it
  at 400k LOC. Where's the threshold?
- **Does lifetime bloat compound?** If token 3 of a test file costs more than
  token 1 — because later tokens only get read when the first fails — the
  lifetime curve isn't linear and every deletion decision changes.

## Style

Match the surrounding entries. Short. Mechanism-first. No marketing adjectives.
Name the mechanism, not the sin: `eagerly-loaded tool schema`, not "bloated
prompt."

If you write about a vendor, write about their number. Several vendors in this
list — Anthropic, Cloudflare, Cognition — publish the measurements this list
depends on, and they are cited as sources constantly.

## Process

1. Open a PR with one coherent addition or correction.
2. One entry per line change, ideally. Batch refactors make review hard.
3. Link rot: if you're updating a stale entry, say what changed and when.
4. Numbers without a stamp decay within weeks in this field. If you're
   re-checking a `measured` entry, that's a high-value PR — send it.
   `check_stamps.py` reports undated entries as one aggregated annotation and
   flags stamps older than twelve months; the weekly date sweep collects the
   full roster in a single `date-rot` issue. It annotates rather than fails
   until coverage justifies enforcing.
5. Put the grade at the end of the entry's **first line**. A split verdict uses
   a compound tag (`[measured]/[asserted]`). The linter only reads that line,
   and so does anyone skimming the list.

CI runs `.github/scripts/check_annotations.py` and `.github/scripts/check_stamps.py`,
which between them check six things: evidence grades, that entries are linked,
same-file `#anchor` targets, relative link targets and their fragments, dates
that go stale, and an undated-entry ceiling per file. The annotation script
reproduces GitHub's slug rules rather than guessing at them — emoji get
percent-encoded, em dashes get dropped, and **runs of spaces are not collapsed**,
so `## Leg 1 — Input` slugs to `#leg-1--input` with two hyphens. Several
cross-references were silently broken before those checks existed; if one flags
you, fix the anchor, not the check.

The relative-link check is the newest and the one that found real defects on the
day it landed: a link *without* a fragment was never validated at all, and
`llms.txt` plus `OPEN-PROBLEMS.md` both pointed at
`harness/docs/context-profiler.md`, a file that did not exist. If a doc is
referenced, it should exist.

A third script, `build_entries.py`, generates `entries.jsonl` — the index over
the entries — and CI fails if the committed index disagrees with the README. It
is generated, not edited; run it after any README change.

The full command list, including the commands to run by hand, lives in
[`AGENTS.md`](AGENTS.md). It is kept there rather than duplicated here: AGENTS.md
is the copy an agent loads on every turn, this file is loaded when a human opens
a PR, and a second copy of the same nine commands is a per-turn tax the repo
already argues against.

### Which file, which format

- **`README.md`** is the list, and the index for the rest. Every bullet beginning
  `- **[` needs a grade on its first line.
- **`TOKENMAXXING.md`** is the negative-result catalog — the blow-ups, with
  their numbers — graded the same way.
- **`ANTI-PATTERNS.md`** and **`OPEN-PROBLEMS.md`** are the two catalogs the
  README used to inline: receipts and cross-links, no `- **[` entries, so they
  run with `--anchors-only`. Numbered items become `### N. Title` headings so
  they can be deep-linked, and the numbers are stable — cite them that way.
  Adding a *number* rather than an entry? The bar is
  [`harness/docs/submit-a-run.md`](harness/docs/submit-a-run.md).
- **`GLOSSARY.md`** is definitions, and carries no grades. It is checked for
  anchors only. Add a term when a contributor reasonably asks what it means —
  the test is whether the README uses it as if it were obvious.
- **`RESOURCES.md`** is reading material, not entries. Its grades describe how
  much weight a source can bear, not a savings claim.
- **`SHOWCASE.md`** is maintainer submissions. The author states their own grade,
  and `[self-reported]` there is a normal, labelled outcome rather than a
  rejection — the header says so, because a weak section that reads as a strong
  one misleads people. An independently measured result is promoted into the main
  list with the measuring party named.

## License

Contributions are accepted under [CC0 1.0](LICENSE), same as the list. No
attribution required, no CLA.
