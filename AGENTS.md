# AGENTS.md

Agent instructions for this repository. Deliberately short — this repo's own
[duplicated-instruction-file anti-pattern](README.md#anti-patterns) treats
`AGENTS.md`/`CLAUDE.md` rules as a per-turn tax, and the profilers in
[Leg 0](README.md#leg-0--measure) are how you check it.

## What this repo is

An awesome list plus its own measurement layer. The content docs are
`README.md`, `TOKENMAXXING.md`, `GLOSSARY.md`, `RESOURCES.md`, `SHOWCASE.md`, and
`CONTRIBUTING.md`; `harness/` and `posts/` hold the paired A/B rig and its
result writeups; `.github/scripts/check_annotations.py` is the CI gate. The rest
is scaffolding and metadata (`CITATION.cff`, `LICENSE`).

`SHOWCASE.md` is the one place a maintainer submits their own tool. The grade is
theirs to state there, which is why the file labels the distinction instead of
blending it with the independently assembled list.

## The one rule

**Every list entry carries an evidence grade.** See
[CONTRIBUTING.md](CONTRIBUTING.md) for the vocabulary.

| Grade | Means |
|---|---|
| `[measured]` | number + stated baseline + method someone could re-run |
| `[self-reported]` | number from the tool's own authors, baseline unstated |
| `[asserted]` | claim with no number |
| `[negative]` | measured, and it did not work |

Split verdicts use a compound tag: `[measured]/[asserted]`.

## Before you open a PR

```sh
python .github/scripts/check_annotations.py README.md                 # must print 0 problems
python .github/scripts/check_annotations.py --anchors-only GLOSSARY.md
python .github/scripts/check_annotations.py RESOURCES.md              # external-resource doc
python .github/scripts/check_annotations.py TOKENMAXXING.md           # negative-result catalog
python .github/scripts/check_annotations.py --allow-empty SHOWCASE.md # maintainer submissions
python .github/scripts/check_annotations.py --urls README.md          # link extraction
```

The script runs the same gate as CI and checks four things: evidence grades,
linked entries, same-file `#anchor` targets, and cross-file `other.md#anchor`
targets. It reproduces GitHub's slug rules rather than guessing at them — emoji
get percent-encoded, em dashes get dropped, and **runs of spaces are not
collapsed**, so `## Leg 1 — Input` slugs to `#leg-1--input` with two hyphens.
Fenced code blocks are blanked before grading, so an entry template quoted as an
example is not itself an entry. If it flags your entry, fix the missing field; if
it flags an anchor, fix the anchor. Do not relax the check.

## Editing the README

- **Mechanism first.** Name what the thing does, not what it's sold as.
  "Wraps tool schemas and expands on demand" — not "powerful AI toolkit."
- **Which leg, which number.** Entries are prefixed with `in` / `out` /
  `lifetime` / `⚡ serve-side` where the delta is ambiguous. Three deltas get
  stated when they differ: `Δ tokens-in │ Δ tokens-out │ Δ $ / Δ wall-clock`.
- **Every technique entry needs an additive clause** — the capability is
  preserved, the unmeasured cost is removed. If you cannot write one, the entry
  belongs in [Anti-patterns](README.md#anti-patterns).
- **Negative results are first-class.** A `[negative]` entry with real
  methodology is worth more than another `[asserted]` one.
- **Numbers decay.** Anything `[measured]` needs model, harness, date, and n
  where you have them. If you're re-checking a stale entry, that's a
  high-value PR.

## Do not

- Add a bare link. An entry without a mechanism description or a grade will be
  sent back.
- Frame an entry as "you have too much stuff." The list's position is that
  capability and minimalism are not opposed; we criticize unmeasured defaults,
  not features.
- Duplicate a neighboring awesome list. Link it and add the token cost, which
  is the part they don't carry.
- Present a `[self-reported]` number as `[measured]`. That applies doubly in
  `SHOWCASE.md`, where the submitter is the author: the grade is theirs to state
  and the file says so. A maintainer entry graded `[measured]` gets its
  methodology reviewed like anyone else's.

## Commit shape

One coherent change per PR. Batch refactors of unrelated entries make review
harder than the change is worth.
