<!--
One coherent change per PR. The grade vocabulary and the additive clause are in
CONTRIBUTING.md; the commands to run are in AGENTS.md.
-->

## What this changes

<!-- The mechanism, not the pitch. One or two sentences. -->

## Which leg, which number

<!--
For an entry: in / out / lifetime / ⚡ serve-side, plus
Δ tokens-in │ Δ tokens-out │ Δ $ / Δ wall-clock where they differ.
Delete this section if the PR is not an entry.
-->

## Checklist

- [ ] Every new or changed entry carries an evidence grade on its **first line** — `[measured]`, `[self-reported]`, `[asserted]`, or `[negative]`
- [ ] `[measured]` states a baseline and a method someone could re-run, with model, harness, date, and n where you have them
- [ ] The entry has an **additive clause** — the capability is preserved, the unmeasured cost is removed
- [ ] The grade names the measuring party; a ledger row needs someone other than the tool's author
- [ ] I ran the gates in [AGENTS.md](AGENTS.md): `check_annotations.py`, `check_stamps.py`, `build_entries.py`, and `pytest harness/tests -q`
- [ ] `entries.jsonl` was regenerated with `build_entries.py` if README entries changed

Negative results are first-class here — a `[negative]` entry with real
methodology is worth more than another `[asserted]` one.

Closes #
