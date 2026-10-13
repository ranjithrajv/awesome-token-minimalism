# Submit a measurement

The runbook behind [SHOWCASE.md](../../SHOWCASE.md): how to get a number that
survives review, and what happens to it afterwards. The repo ships its own
measurement rig — [token-harness](../../README.md) — so a maintainer does not have
to take the list's word for how a claim should be built.

## Why bother

Three popular token-saving tools went through one paired A/B harness. One
delivered −8.5% against a −65% claim, one was *more expensive* than baseline, and
one underdelivered on code size but did deliver on cost. Nobody knew in advance.
The list grades numbers because the gap between advertised and measured is the
least-measured quantity in the field — see the
[token ledger](../../README.md#token-ledger).

A number you publish against your own tool is the strongest thing a maintainer
can submit, and it is also the only route into the main list.

## The four things a reviewer checks

| # | Field | What satisfies it | What doesn't |
|---|---|---|---|
| 1 | Baseline | the arm you compared against, by name | "before" |
| 2 | Method | the harness, the task suite, and where both live | "we benchmarked it" |
| 3 | Stamp | model, harness version, date, `n`, and a significance test where you have one | a percentage with no `n` |
| 4 | Measuring party | who ran it — you, or someone else | left blank |

Field 4 is the one people skip, and it is the one that decides the grade. An
author-published number with 1–3 present is `[self-reported]`: real evidence,
correctly labelled. It becomes `[measured]` when a party other than the tool's
author reproduces it.

## Running it yourself

The harness is a paired A/B rig: every task runs under both arms, the per-task
difference is the unit of analysis, and a separate quality guard has to hold.
That design is what stops a token reduction from looking like a win because the
tool got worse at the task.

```sh
cd harness
pip install -e ".[dev]"
token-harness run \
  --tasks tasks/swebench_lite.json \
  --config configs/your-tool.json \
  --output report.json

token-harness report --input report.json
```

48 real GitHub issues across twelve repositories, pinned model, `tiktoken`
counting, `n` and p-values in the report. A tool plugs in as a task executor — a
function `(task, arm) -> TaskResult` returning `tokens_in`, `tokens_out`,
`cost_usd`, `wall_clock_s`, and `quality_score`. The full executor contract is in
**[harness/README.md](../../harness/README.md#write-your-own)**.

Three traps worth knowing before you spend an afternoon:

- **Output tokens may not be reported.** Some agent CLIs emit no output-token
  count; the Copilot CLI executor estimates at 4 chars/token and says so in the
  report. State your estimator, don't leave it implied.
- **Rate limits cap your sample.** A free tier's TPM limit decides how many
  tasks you can run, which decides your `n`. Report the cap.
- **Quality is a guard, not a footnote.** A tool that cuts tokens and silently
  drops a check is `[negative]`, not `[measured]`. Record the guard even when it
  looks unflattering.

## If you can't run a harness

Say so, and submit anyway. What disqualifies an entry is a *number with no
baseline* — "90% savings" against what, measured how? A figure you can source to
a public write-up, a paper, or a benchmark file, with the party named, is a
usable `[self-reported]` entry. An entry that names its own limits is worth more
than one that doesn't.

## What happens after you open the PR

1. **Review of the grade, not of the tool.** A `[measured]` submission gets its
   methodology checked like any other; a `[self-reported]` one gets labelled as
   such. Neither is a demotion.
2. **Leaderboard admission.** A run with a baseline, a method, and a quality
   guard earns a row in [harness/LEADERBOARD.md](../../harness/LEADERBOARD.md),
   grouped by harness. Rows from different harnesses are not compared to each
   other, and neither are the two groups.
3. **Promotion.** An independently measured result is moved into the main list,
   with the measuring party named — see the
   [token ledger](../../README.md#token-ledger). That migration is the point of the
   showcase, not a correction of it.
4. **Staleness is not removal.** If a number goes stale, say what changed and
   when. Silence is the only reason an entry leaves.

## Fastest path

Open an issue with the
[showcase submission form](../../.github/ISSUE_TEMPLATE/showcase-submission.yml) and
the required fields, then send the PR. One entry per PR.

---

Part of [Awesome Token Minimalism](README.md).
