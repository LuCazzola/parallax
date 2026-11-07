---
name: sync
description: Use in a repo with a .parallax.toml when code changed and docs may need to follow, when a hook says to run parallax:sync, or when finishing a change.
---

# Sync

Only for a repo with `.parallax.toml` at its root; elsewhere this skill does not apply, so carry on
normally. `docs/` below means the `docs_dir` set there.

**The code is the oracle, docs follow, and neither implies correctness.** Sync moves pages
to what the code does now. It edits docs only, never code.

## Steps

1. Read the change: `git status` and `git diff`, plus any commits made this turn.
2. Find the pages that state something about it: grep `docs/` for each changed path (User
   Guide pages list theirs on the `Code:` line) and for the names, flags, defaults, config
   keys and formats that changed. Include `CLAUDE.md`. Done when every changed thing has
   been searched for.
3. Edit each stale statement to what the code does now, in the smallest edit, leaving the
   surrounding prose as it is. Update `docs/agent-guide/map.md` when files moved.
4. Add a page or section only when the change introduces a new subsystem or design decision.
   Place it by meaning (below). A reason the user gave you counts as confirmed; a reason you
   inferred gets the mark:

   ```markdown
   !!! warning "Inferred, not confirmed"
       <the reason>
   ```

5. Run `python3 docs/agent-guide/check_docs.py` and the strict build from
   `docs/agent-guide/testing.md`. Fix what they report by editing docs: a missing path means the
   page is wrong.
6. Call `parallax:dive` when what you wrote looks wrong, when you are unsure you read the
   code correctly, or when the change touches a design decision or new subsystem.
7. Report the pages changed, or "nothing to update" when no page stated anything about it.

## The page moves, always

Every stale statement is corrected in this sync, including when the new behaviour looks like
a bug or you cannot tell what was intended. State what the code does, in plain words with the
value it has: "Login tokens have a TTL of 0 seconds (`TOKEN_TTL_S`)." A strange statement in
the docs is useful, because it is what makes someone ask why. Then step 6 raises the doubt.

| Thought | Reality |
|---|---|
| "I can't tell what this value is meant to mean, so I'll leave the sentence" | Quote the value. A stale sentence hides the change. |
| "This looks like a bug, I'll wait for an answer first" | Update the page, then call `parallax:dive`. Both happen now. |
| "The doc is right, so the code should change" | The code is the oracle. A doubt goes to `dive`; the code stays. |
| "No time before the release" | A one-line edit is the fast path. |

## Placing new material

Group by how the system is understood, never by folder or file type. The nearest section's
index says what belongs there. If a page fits nowhere, the grouping may be wrong: propose
regrouping to the user. User Guide pages open with a `Code:` line, explain why in lean prose,
and say things a reader could disagree with. Agent Guide pages hold what the code cannot say
quickly, and point to code rather than paraphrasing it. Keep out counts that rot and
per-change log entries.
