# Showcase

A section for **project maintainers** to list their own tools.

The rest of this list is independently assembled: entries are found, read, and
graded by someone other than the tool's author. This section is different — the
author submits, and the grade is theirs to state. That difference is stated
plainly rather than hidden, because a self-reported number and an independently
measured one are not the same kind of evidence.

| | Main list | Showcase |
|---|---|---|
| Who submits | anyone | the project maintainer |
| Who grades | an independent reader | you, about your own tool |
| Baseline | stated and checkable | stated, not independently checked |
| Typical grade | `[measured]` | `[self-reported]` |

A showcase entry that gets independently measured later and reaches the main
list's bar will be moved there. That migration is the point — not a demotion.

## What qualifies

Four criteria. All four, no exceptions.

1. **FOSS, or a meaningful free tier.** Open source preferred; a free tier that
   covers real use is acceptable. Closed-source with no free tier does not
   qualify — the reader can't verify the claim, and neither can you.
2. **An additive clause.** The capability is preserved, the unmeasured cost is
   removed. "You have too much stuff" does not qualify — that's the framing this
   list exists to argue against.
3. **A number with a baseline.** Any size. `−8% on a 200-task benchmark` is
   fine. `Much more efficient` is not an entry, it is an advertisement.
4. **The repo or docs are linked.** Not the marketing page. The README, the
   benchmark file, the paper. The thing a reader can check.

## What does not qualify

- **A number with no baseline.** `90% token savings` against what, measured how?
- **A savings counter.** Your tool's own dashboard reporting tokens saved is not
  evidence — the bill is. See [Token ledger](README.md#token-ledger) for three
  tools whose counters disagreed with the bill.
- **A vendor comparison without a harness.** "Faster than X" needs the same
  tasks, the same model, and a stated metric.
- **A press release with a chart in it.** If you can't name the baseline, it
  isn't a number yet.

## Entry format

Copy this exactly. The linter reads the first line, so the grade goes there.

```markdown
- **[project-name](https://github.com/owner/repo)** — one line on the
  mechanism: what it does, not what it's sold as. `Δin −85%` `Δout −98%`
  `Δ$ −60%` — baseline: what you compared against, on what tasks.
  `[self-reported]` — model, harness, date, n. Stamp what you actually ran.
```

**If you measured it properly** — baseline stated, method re-runnable, n and a
significance test where you have them — put `[measured]` on the first line and
expect a review of the methodology. That's the only route into the main list,
and it's worth taking: `[measured]` is the strongest grade this list has.

## Current showcase

Nothing here yet. Be the first, or the second — a showcase with several entries
is more useful to a reader than one with none.

Open a PR against [`SHOWCASE.md`](SHOWCASE.md). One entry per PR. If a number
is stale, say what changed and when — staleness is not a reason to remove an
entry, silence is.

---

## Why this section exists

An awesome list assembled only by third parties has a selection problem: the tools
that most need to be listed are often the ones nobody has heard of, and the tools
everyone lists are the ones that already have a marketing budget. Maintainers
know their tools best, including the ones with an honest caveat nobody else would
write down.

The cost of opening this door is real — self-reported numbers are weaker evidence,
and a weak section can read as a strong one. The mitigation is structural rather
than editorial: the distinction is in the header, the grade vocabulary is the
same one the main list uses, and `[self-reported]` is never presented as
`[measured]`. A reader who knows the difference between the sections is not misled.
A reader who doesn't is better served by an obvious label than by a quiet omission.

Related: [Contributing](CONTRIBUTING.md) · [Token ledger](README.md#token-ledger) ·
[Evidence grades](README.md#evidence-grades)