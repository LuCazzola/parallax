---
name: gap
description: Use in a repo with a .parallax.toml when someone's picture of the system differs from the docs or code, such as "that's not how I thought this worked", "I imagined X", "why does it do Y", or a surprising result or doubtful design.
---

# Gap

Only for a repo with `.parallax.toml` at its root; elsewhere this skill does not apply, so carry on
normally. `docs/` below means the `docs_dir` set there.

The person's picture differs from the docs or code. **The code is the oracle for what happens,
and neither implies correctness.** The picture is evidence, so find out what the gap means.

A gap ends in a verdict and a docs edit or ticket. Code stays exactly as it is, even when the
fix is one line and obviously right. Fixing code is a separate request: offer it, and wait for
the person to ask.

## Steps

1. Read the code the remark touches, then the pages about it. Done when you can quote what
   the code does.
2. Give one verdict per remark:

| Verdict | Means | Action |
|---|---|---|
| **Stale doc** | Code is as intended, the page is out of date | Fix the page toward the code |
| **Real issue** | Code does not do what it is meant to | Open an issue via `parallax:ticket`; the page states the actual behaviour and links the issue |
| **Design flaw** | Code does what was designed, and the design looks wrong | Open an idea via `parallax:ticket`, or an issue if it does harm |
| **Misunderstanding** | Code and page agree and are fine | Explain with the reasons, and sharpen the page if it invited the wrong reading |

3. Report each verdict with the code you read, what you did, and any offer to fix.

When the verdict is unclear, ask.

If the person reports a doubt about a design, that is enough for a **design flaw** verdict even
when the page gives a reason for the design: the reason is a trade-off they may no longer want.

| Thought | Reality |
|---|---|
| "The doc states the intent, so I'll fix the code to match" | Docs never drive code. Open the issue. |
| "It's a one-line bug, faster to just fix it" | Open the issue, offer the fix, wait. |
| "The doc explains the design, so there's nothing to record" | Their doubt is worth keeping. Open the idea. |
