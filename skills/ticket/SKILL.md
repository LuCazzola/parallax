---
name: ticket
description: Use in a repo with a .parallax.toml when something should be kept for later, such as "we should someday", "note that" or "park this", when a bug is noticed and left unfixed, or when parallax:sync, gap or dive has a suspicion to record.
---

# Ticket

Only for a repo with `.parallax.toml` at its root; elsewhere this skill does not apply, so carry on
normally. `docs/` below means the `docs_dir` set there.

Keep the thought and carry on with the task at hand. Capture here; designing the idea is a
separate job. The scripts and their rules are in `docs/agent-guide/tickets/ideas.md`.

## Steps

1. **Pick the kind.** Nothing is broken yet: `idea`. Something is broken or loose: an issue,
   tiered `critical` (breaks a run, or may harm people, systems or data), `wanted`, or `minor`.
2. **Separate what you know.** The issue text holds only what was observed. How to see it
   again goes in `--repro`; your guess at the reason goes in `--cause`.
3. **Check the gate.** Ideas stay in the repo, so file them straight away. For an issue, read
   `auto_file_issues` in `.parallax.toml` and run
   `gh repo view --json visibility`:

| `auto_file_issues` | Repo | Action |
|---|---|---|
| `always` | any | File |
| `private` (default) | private | File |
| `private` (default) | public | Show the draft and ask first |
| `never` | any | Show the draft and ask first |
| any | not on GitHub | Offer an idea instead |

   An issue on a public repo publishes paths and behaviour under the user's name, and that is
   hard to undo. The gate holds inside a sync turn and under time pressure.

4. **File it** with `python3 docs/agent-guide/tickets/open_ticket.py`, and report the ID.
