# Contributing

Thanks for considering a contribution. This list has one editorial rule that
matters more than any other, and this file is mostly about it.

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
| **Token ledger** | has been independently measured against its claim |

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
belongs in [Anti-patterns](README.md#anti-patterns). Both are fine outcomes. The
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

The list has a standing [Open problems](README.md#open-problems) section with
seven questions nobody has answered. If you can answer one — even partially — that
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
5. Put the grade at the end of the entry's **first line**. A split verdict uses
   a compound tag (`[measured]/[asserted]`). The linter only reads that line,
   and so does anyone skimming the list.

CI runs one script, `.github/scripts/check_annotations.py`, which checks four
things: evidence grades, that entries are linked, same-file `#anchor` targets,
and cross-file `other.md#anchor` targets. It reproduces GitHub's slug rules
rather than guessing at them — emoji get percent-encoded, em dashes get dropped,
and **runs of spaces are not collapsed**, so `## Leg 1 — Input` slugs to
`#leg-1--input` with two hyphens. Several cross-references were silently broken
before those checks existed; if one flags you, fix the anchor, not the check.

```sh
python .github/scripts/check_annotations.py README.md                 # grades + anchors
python .github/scripts/check_annotations.py --anchors-only GLOSSARY.md
python .github/scripts/check_annotations.py --urls README.md          # link health
```

### Two files, two formats

- **`README.md`** is the list. Every bullet beginning `- **[` needs a grade on
  its first line.
- **`GLOSSARY.md`** is definitions, and carries no grades. It is checked for
  anchors only. Add a term when a contributor reasonably asks what it means —
  the test is whether the README uses it as if it were obvious.

## License

Contributions are accepted under [CC0 1.0](LICENSE), same as the list. No
attribution required, no CLA.
