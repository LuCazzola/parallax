---
name: sync
description: Use in a repo with docs/parallax/parallax.toml when code changed and docs may need to follow, when a hook says to run parallax:sync, or when finishing a change.
---

# Sync

Only for a repo with `docs/parallax/parallax.toml`; elsewhere this skill does not apply, so carry
on normally.

**The code is the oracle, docs follow, and neither implies correctness.** Sync moves pages
to what the code does now. It edits docs only, never code.

## Steps

1. Read the change: `git status` and `git diff`, plus any commits made this turn.
2. Find the pages that state something about it: grep `docs/parallax/pages/` for each changed path (User
   Guide pages list theirs on the `Code:` line) and for the names, flags, defaults, config
   keys and formats that changed. Include `CLAUDE.md`. Done when every changed thing has
   been searched for.
3. Edit each stale statement to what the code does now, in the smallest edit, leaving the
   surrounding prose as it is. A stated reason stays unless the code contradicts it. Update `docs/parallax/pages/agent-guide/map.md` when files moved.
4. Add a page or section only when the change introduces a new subsystem or design decision.
   Place it by meaning (below). A reason the user gave you counts as confirmed; a reason you
   inferred gets the mark:

   ```markdown
   !!! warning "Inferred, not confirmed"
       <the reason>
   ```

5. Run `python3 docs/parallax/tools/check_docs.py` and the strict build from
   `docs/parallax/pages/agent-guide/testing.md`. Fix what they report by editing docs: a missing path means the
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
regrouping to the user. Agent Guide pages hold what the code cannot say quickly, and point to
code rather than paraphrasing it. Keep out counts that rot and per-change log entries.

## Writing the User Guide

The User Guide exists so a person can hold a picture of the system and notice where it differs
from theirs. They read it front to back, like a book, so the nav order is the reading order:
the whole system first, then each part in the order a change or a request travels through it.
Sections are the chapters: a section's index opens the chapter with the picture of that part,
and its pages follow in reading order. The guide's index draws the whole system in one diagram
and gives the reading order with the reason for it.

Every other User Guide page has these parts, in this order:

1. The `Code:` line.
2. **Where we are:** one or two sentences that pick up from the page before it in the nav and
   name the question this page answers.
3. **The picture**, when the page describes steps, branches, states, parts that talk to each
   other, or a value changing over time. It uses the words the prose uses.
4. **The reasons:** lean prose that walks the picture in the picture's order and explains why.
   The picture carries the shape; the prose carries the commitments. Each statement is one a
   reader could find wrong: it names the value or condition in the code and says what follows
   from it, as in "Uploads above 50 MB are rejected (`MAX_UPLOAD_MB`) before the file is read,
   so a too-large upload fails with no entry in the audit log." Follow each branch and limit to its
   consequence, the odd ones above all. Plain words, exact facts.
5. **Where next:** a closing line linking the next page in the nav, with the question it
   picks up.

A page too long for one picture is split into numbered sections (`## 1) Title {#anchor}`), one
per step of its story, and each section gets parts 3 and 4.

## Pictures

People take in a structure faster from a picture, and a picture written as text is one an
agent can read, grep and correct. Use two kinds:

- **Boxes and arrows** (a flow, states, a sequence, parts and their links): a ` ```mermaid `
  block. Tint a group with `style <id> fill:#2f6db326,stroke:#2f6db3`.
- **What Mermaid cannot draw** (a value over time, a timeline, geometry): an inline SVG sketch.

  ```html
  <div markdown="0">
  <svg class="parallax-fig" viewBox="0 0 860 200" width="100%" role="img"
       aria-label="One sentence saying what the figure shows.">
  <line class="grid" x1="110" y1="28" x2="110" y2="190"/>
  <path class="s1" d="M110,150 C200,150 240,70 400,70"/>
  <circle class="f2" cx="400" cy="70" r="5"/>
  <text class="note" x="414" y="74">reply arrives</text>
  </svg>
  </div>
  ```

  It is a sketch: a few shapes and curve commands, short enough to read as text. The classes
  come from `stylesheets/extra.css` and follow light and dark mode: `s1` to `s6` stroke,
  `f1` to `f6` fill, `grid`, `axis`, `note`, `faint`, `dash`. A process in steps gets one small
  figure per step, on the same axes.

A colour means one thing per picture, and a line under the picture says what. A picture states
things, so it follows the code like any sentence: step 3 corrects a stale label, arrow or
`aria-label`. A new page goes where the story needs it in the nav, and the pages on either
side get their "where we are" and "where next" lines rewritten to include it.
