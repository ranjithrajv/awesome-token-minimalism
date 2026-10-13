# AGENTS.md

Agent instructions for this repository. Deliberately short — this repo's own
[duplicated-instruction-file anti-pattern](ANTI-PATTERNS.md) treats
`AGENTS.md`/`CLAUDE.md` rules as a per-turn tax, and the profilers in
[Leg 0](README.md#leg-0--measure) are how you check it.

## What this repo is

An awesome list plus its own measurement layer. The content docs are
`README.md`, `TOKENMAXXING.md`, `GLOSSARY.md`, `RESOURCES.md`, `SHOWCASE.md`,
`ANTI-PATTERNS.md`, `OPEN-PROBLEMS.md`, and `CONTRIBUTING.md`; `harness/` and
`posts/` hold the paired A/B rig and its result writeups;
`.github/scripts/check_annotations.py` and `check_stamps.py` are the CI gate.
The rest is scaffolding and metadata (`CITATION.cff`, `LICENSE`).

`README.md` is the index and carries the entries; `entries.jsonl` is the
generated index over those entries — name, URL, section, grade, date, one line
each — so a qualification question costs ~10k tokens instead of the list's
~37k. Regenerate it with `.github/scripts/build_entries.py`; never hand-edit it,
CI diffs it.
`ANTI-PATTERNS.md` and
`OPEN-PROBLEMS.md` are the two catalogs it points at (nineteen unmeasured
defaults, sixteen unmeasured questions), one file each, no details toggle.
`SHOWCASE.md` is where a maintainer submits their own tool and
`harness/docs/submit-a-run.md` is the runbook for a number that survives review
— the grade is theirs to state, which is why the file labels the distinction.
`llms.txt` is the machine-readable index; add new docs there.

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
python .github/scripts/check_annotations.py --anchors-only ANTI-PATTERNS.md  # defaults catalog
python .github/scripts/check_annotations.py --anchors-only OPEN-PROBLEMS.md  # gaps catalog
python .github/scripts/check_annotations.py --allow-empty SHOWCASE.md # maintainer submissions
python .github/scripts/check_annotations.py --anchors-only llms.txt   # machine-readable index
python .github/scripts/check_stamps.py README.md              # stamps: stale or undated
python .github/scripts/build_entries.py                             # after any README edit
python .github/scripts/build_entries.py --check           # same gate CI runs
python .github/scripts/check_annotations.py --urls README.md          # link extraction
pytest harness/tests -q                                             # harness + checker tests
```

The two catalogs carry receipts and cross-links but no `- **[` entries, so they
run with `--anchors-only` — the same mode as `GLOSSARY.md`. Do not add
`--allow-empty` to force them through `check_entries`; there is nothing there to
grade.

**Dates are the fourth check.** `check_stamps.py` warns on undated entries and on
stamps older than twelve months, and *fails* when a file's undated count goes
over the ceiling in `MAX_UNDATED`. Lower that ceiling in the same PR that adds
the dates — it is a ratchet, not a target, and the number it is holding (150 of
154 README entries) is the repo's biggest credibility gap.

**Relative links are checked, not assumed.** Every `](path)` that points inside
this repo must resolve, with or without a `#fragment`. Before that check existed,
`llms.txt` and `OPEN-PROBLEMS.md` both shipped pointing at
`harness/docs/context-profiler.md` — a file that did not exist. A doc that is
referenced belongs in `llms.txt`; a doc that has not been written does not get a
link.

The script runs the same gate as CI and checks six things: evidence grades,
linked entries, same-file `#anchor` targets, relative link targets with their
fragments, dates that go stale, and the per-file undated ceiling. It reproduces
GitHub's slug rules rather than guessing at them — emoji get percent-encoded, em
dashes get dropped, and **runs of spaces are not collapsed**, so
`## Leg 1 — Input` slugs to `#leg-1--input` with two hyphens.
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
  belongs in [Anti-patterns](ANTI-PATTERNS.md).
- **Negative results are first-class.** A `[negative]` entry with real
  methodology is worth more than another `[asserted]` one.
- **Numbers decay.** Anything `[measured]` needs model, harness, date, and n
  where you have them. If you're re-checking a stale entry, that's a
  high-value PR.
- **Name the measuring party.** A `[measured]` ledger row needs someone other
  than the tool's author behind it; an author-published number with a stated
  baseline and method is `[self-reported]`, however well documented. Say which
  one it is.

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
