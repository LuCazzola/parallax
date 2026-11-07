---
name: dive
description: Use when docs and code may agree on something wrong, when a docs sync wrote something that looks off or touched a design decision or new subsystem, or when asked whether the docs are healthy, in place, or need a whole-repo check.
---

# Dive

**The code is the oracle, docs follow, and neither implies correctness.** A dive asks two
questions: do docs and code agree, and even if they do, does what they agree on look like
a bug? Dive changes nothing itself and never changes code.

## Steps

1. Pick the mode: **targeted** when a sync sent you here, **whole-repo** when asked about
   the docs overall or when `parallax:setup` is porting.
2. Run `python3 docs/agent-guide/check_docs.py` and keep its output.
3. Dispatch the `skeptic` subagent with the brief below. Done when it returns a verdict
   block for every claim.
4. Act on the verdicts:

| Verdict | Targeted | Whole-repo |
|---|---|---|
| `mismatch` | Return it to sync, which fixes the page toward the code | Goes in the drift report |
| `agrees-suspect` | Open a ticket through `parallax:ticket` with the `Bug if` and `Confirm` lines; the page stays as it is | Same, after the user's decision on its group |
| `agrees-nothing-suspicious` | Report it as "nothing found" | Count only |
| `cant-tell` | Report what is missing | Goes in the drift report |

A suspicion is a lead: its issue stays `needs-triage` until there is evidence. A page that
accurately describes a suspected bug is correct and stays as it is, because it describes what
the code does; it changes when the code does.

## Briefs

**Targeted:** the changed paths, the pages touched, and what sync thought, labelled as
claims to test. List each statement from those pages as a claim.

**Whole-repo:** every page outside `investigations/` and `superpowers/`, split into one
skeptic per section of the docs so each stays focused. Also ask it to check the structure:
sections grouped by meaning, each index saying why the section exists, the map covering the
top-level code, API stubs, `.parallax.toml`, and the stub in `CLAUDE.md`.

## Drift report (whole-repo)

Nobody may remember why old code is the way it is, so ask once per group, not per mismatch.
Group mismatches by likely cause, and for each group give: the cause, the pages, one example,
and the two decisions to take: update these pages now, and does this deserve a ticket. The
outcome of a decision is a docs edit or a ticket. Edit pages only after the decision.
