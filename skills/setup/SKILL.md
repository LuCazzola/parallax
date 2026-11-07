---
name: setup
description: Use once per repo to give it Parallax docs, in a new repo or one with existing docs.
disable-model-invocation: true
---

# Setup

**The code is the oracle, docs follow, and neither implies correctness.** Setup never changes
code. Templates are in `templates/`, two levels above this skill's base directory.

## 1. Look

Read the repo: language, source roots, docs, `CLAUDE.md`, remote and visibility
(`gh repo view --json visibility`). Done when you can name each.

## 2. Ask

Ask all of these in one message, and wait for the answers.

- **Hosting.** GitHub Actions (recommended), local, or elsewhere. If the repo is private, say
  this first: Pages on a private repo needs a paid plan, and the site is normally public anyway
  unless on Enterprise, so internals would be published.
- **Existing docs**, only if the repo has them. Port everything into Parallax (recommended),
  keep both side by side (Parallax gets its own folder and site, the existing site stays
  untouched), or abort. If a public site is involved and the choice is to port, warn that both
  guides would be published with it.

On abort, stop with the working tree unchanged.

## 3. Show the mapping

Existing docs only. Present a table of every current page and where it goes, grouped by meaning,
and wait for approval. Every page appears in it.

## 4. Write

1. Copy `templates/` into the repo, leaving out `CLAUDE-stub.md`. Fill `{{site_name}}`,
   `{{repo_url}}`, `{{source_root}}`. Hosting decides the last files: Actions keeps
   `.github/workflows/docs.yml`; local keeps `docker-compose.docs.yml` and drops the workflow;
   elsewhere drops both.
2. Python: add one `docs/agent-guide/api/<package/as/path>/index.md` per package, with a
   `::: <package>` block per module, and list each in the nav. Other languages: use a generator
   if one fits, otherwise remove `mkdocstrings` and rely on the map.
3. Port by moving pages to the approved places with `git mv`, meaning unchanged.
4. Fill the guides from the code, following the page comments in the templates and the writing
   rules in `parallax:sync`. Create pages only for things that exist. Group by meaning, and give
   each section an index saying why it exists. Remove the `<!-- parallax: -->` comments you
   fill. Check each statement you write against the code.

## 5. Keep the reasons honest

Code shows what happens, not why. Every reason in the User Guide is one of:

- **Written by a person** in the existing docs: keep it as confirmed, unless the code contradicts it.
- **Given by the user:** confirmed.
- **Inferred by you:** mark it, and only a person's word removes the mark.

```markdown
!!! warning "Inferred, not confirmed"
    <the reason>
```

## 6. Report drift

Moved pages keep their statements, including wrong ones. Run the whole-repo pass of
`parallax:dive` and bring its drift report to the user, grouped by likely cause. Nothing in it is
rewritten before their decision, and the outcome is a docs edit or a ticket.

## 7. Finish

1. Add `templates/CLAUDE-stub.md` to `CLAUDE.md`, creating the file if absent, replacing anything
   already between the `parallax:` markers. If `CLAUDE.md` holds other doc rules, propose
   replacing them with the stub; leave them in place until the user agrees.
2. On GitHub, create the ticket labels with `gh label create --force`: `Prio:CRITICAL`,
   `Prio:WANTED`, `Prio:MINOR`, `needs-triage`.
3. Run `python3 docs/agent-guide/check_docs.py` and the strict build from
   `docs/agent-guide/testing.md`. Anything still failing belongs in the drift report.
4. Report what changed, then list every inferred reason and ask the user to confirm or correct it.
   For Actions, add that Pages' source must be set to GitHub Actions in the repo's settings.

Run again on a repo already set up, only the stub between its markers and the drift report change.
