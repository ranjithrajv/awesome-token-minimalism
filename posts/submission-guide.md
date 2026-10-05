# Submission Guide: "The Seven-Word Baseline"

Ready-to-publish content for Hacker News, X, and blog platforms.

---

## Hacker News

**Title:**
```
A seven-word prompt saves 418 tokens per call — but only 10 per agent session
```

**URL:** (link to your blog post or GitHub repo)

**Comment (post as a comment on your own submission, or use as the "Ask HN" text):**

```
We put three popular token-saving tools (ponytail, caveman, rtk) through a
paired A/B measurement — same tasks, same model, same Docker sandbox, real
billed trials, significance tests. Then we added a third arm that cost nothing:
a seven-word system prompt ("Follow YAGNI, prefer one-liners").

Results:
- ponytail: −54% code, −20% cost (advertised) → −15.4% code, −10.3% cost (measured)
- caveman: −65% output (advertised) → −8.5% (measured)
- "Follow YAGNI": −33% code, −21% cost, −30% time — matched ponytail on cost and time

We then ran the instruction through our own paired harness on 48 real GitHub
issues (Groq): 418.25 output tokens saved per task (p=0.0001). Earlier pilots
measured 522 on 12 tasks (p=0.0004) and 268.67 on 24 (p=0.053) — the smaller
samples overstated the effect. The surface and the sample size both matter.

We also ran the same tasks through GitHub Copilot CLI. A single "echo hello"
task cost 17,549 tokens ($0.055 at Sonnet-5 list rates as a proxy). Tool schemas
alone: 8,521 tokens — a permanent tax on every session. The capability is real.
The question is whether loading all 23 eagerly is the only way to provide it.
Route them on demand: capability preserved, cost removed.

The seven-word prompt was free, instant, and model-agnostic. It was also the
only arm that wrote an unsafe function (dropped a path-traversal check once
in four runs).

The gap between advertised and measured savings is the least-measured quantity
in the entire field. Of three popular token tools put through one paired A/B
harness, one was more expensive than baseline (+7.6% cost, p=0.004).

Full methodology: model, harness, date, n, p-values, quality guard.
https://github.com/ranjithrajv/awesome-token-minimalism
```

---

## X / Twitter

**Thread (post as a thread, first tweet is the hook):**

**Tweet 1:**
```
We measured two popular token-saving tools in a paired A/B test.

A seven-word prompt beat both.

Here's what we found 🧵
```

**Tweet 2:**
```
The setup:
• ponytail (−54% code, −20% cost advertised)
• caveman (−65% output advertised)
• "Follow YAGNI, prefer one-liners" (free)

Same tasks, same model, same Docker sandbox, real billed trials, p-values.
```

**Tweet 3:**
```
Results:
• ponytail: −15.4% code, −10.3% cost (measured)
• caveman: −8.5% (measured)
• 7-word prompt: −33% code, −21% cost, −30% time

The prompt matched ponytail on cost. For free.
```

**Tweet 3.5:**
```
We ran a paired A/B: 48 SWE-bench tasks through Groq, 12 through Copilot CLI.

The 7-word prompt saves 418 output tokens per task on single API calls (p=0.0001).

But only 9.58 on full agent sessions (p=0.52).

The measurement surface matters.
```

**Tweet 4:**
```
The catch: the 7-word prompt was also the only arm that wrote an unsafe
function — dropped a path-traversal check once in four runs.

The cheapest intervention is often a sentence. But the cheapest intervention
is not always the safest one.
```

**Tweet 5:**
```
The gap between advertised and measured savings is the least-measured
quantity in the entire field.

Of three popular token tools put through one paired A/B harness, one was
MORE EXPENSIVE than baseline (+7.6% cost, p=0.004).

Full methodology + open problems:
https://github.com/ranjithrajv/awesome-token-minimalism
```

---

## Blog Post (Medium / Dev.to / Personal)

Use `posts/the-seven-word-baseline.md` as the base. Add:

1. **Hero image:** The ASCII bar chart from the README token ledger
2. **Author bio:** One line linking to the repo
3. **Tags:** `#llm` `#tokens` `#ai` `#measurement` `#benchmark`

---

## Reddit

**Subreddits:** r/LocalLLaMA, r/ClaudeAI, r/MachineLearning, r/programming

**Title:**
```
[Project] We measured two token-saving tools in a paired A/B test — a seven-word prompt beat both
```

**Body:** Use the HN comment text above.

---

## Timing

- **Hacker News:** Tuesday–Thursday, 8–10am ET (peak traffic)
- **X:** Weekdays, 9am–12pm ET
- **Reddit:** Weekdays, 8–10am ET
- **Dev.to:** Any time, but Tuesday–Thursday gets more traction

## After posting

1. Pin the post on your X profile for 48 hours
2. Cross-post to relevant Discord/Slack communities
3. Submit to relevant newsletters (e.g., Import AI, The Batch)
4. Monitor comments and respond with data — the methodology is the moat
