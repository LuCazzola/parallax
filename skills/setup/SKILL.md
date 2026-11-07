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
(`gh repo view --json visibility`), default branch, and generated files that are neither
ignored by git nor source (logs, lockfiles). Check `python3 --version`: below 3.11 the hook and
checks do not run, so tell the user first. Done when you can name each.

## 2. Ask

Ask all of these in one message, and wait for the answers.

- **Hosting.** GitHub Actions (recommended), local, or elsewhere, and if elsewhere, the target.
  If the repo is private, say this first: Pages on a private repo needs a paid plan, and the site is normally public anyway
  unless on Enterprise, so internals would be published.
- **Existing docs**, only if the repo has them. Port everything into Parallax (recommended),
  keep both side by side (Parallax gets its own folder and site, the existing site stays
  untouched), or abort. If a public site is involved and the choice is to port, warn that both
  guides would be published with it. If the repo already publishes to Pages, warn that one repo
  has one Pages site, so side by side needs local or elsewhere hosting.

On abort, stop with the working tree unchanged.

## 3. Show the mapping

Existing docs only. If they have uncommitted changes, ask the user to commit them first, so
nothing here can lose them. Then present a table of every current page and where it goes, grouped
by meaning, and wait for approval. Every page appears in it, and so does every existing file a
template would land on (`docs/index.md`, `mkdocs.yml`, a workflow) with how it merges.

## 4. Write

1. Copy `templates/` into the repo, leaving out `CLAUDE-stub.md`. An existing file is never
   overwritten: skip it, and merge it as the mapping says. Fill `{{site_name}}`, `{{repo_url}}`
   (drop the line if there is no remote), `{{source_root}}`, `{{default_branch}}`. Set `ignore` in
   `.parallax.toml` to the generated files you found. Hosting decides the last files: Actions
   keeps `.github/workflows/docs.yml`; local drops the workflow, and keeps
   `docker-compose.docs.yml` if the repo uses Docker, otherwise the `uvx` serve command in
   `testing.md` is enough; elsewhere drops both, and `testing.md` records the target and the
   build command.
   **Side by side:** copy everything under a `parallax/` folder instead, so the config is
   `parallax/mkdocs.yml`, set `docs_dir = "parallax/docs"` and add `"parallax/*"` to `ignore` in the
   root `.parallax.toml`, and write that path into the stub, the `testing.md` commands and the
   `ideas.md` commands. Existing docs stay where they are, unmoved.
2. Python: add one `docs/agent-guide/api/<package/as/path>/index.md` per package, with a
   `::: <package>` block per module, and list each in the nav. Other languages: use a generator
   if one fits, otherwise remove `mkdocstrings` and rely on the map.
3. Port by moving pages to the approved places with `git mv`, meaning unchanged. Convert other
   formats (`.rst`, `.mdx`) to Markdown, keeping every statement; a file MkDocs cannot render does
   not count as ported.
4. Fill the guides from the code, following the page comments in the templates and the writing
   rules in `parallax:sync`. Create pages only for things that exist, and delete template pages with nothing to say, with their
   nav entries. Group by meaning, and give
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

## 6. Add the stub

1. Add `templates/CLAUDE-stub.md` to `CLAUDE.md`, creating the file if absent, replacing anything
   already between the `parallax:` markers. If `CLAUDE.md` holds other doc rules, propose
   replacing them with the stub; leave them in place until the user agrees.

## 7. Report drift

Moved pages keep their statements, including wrong ones. Run the whole-repo pass of
`parallax:dive` and bring its drift report to the user, grouped by likely cause. Nothing in it is
rewritten before their decision, and the outcome is a docs edit or a ticket.

## 8. Finish

1. On GitHub, create the ticket labels with `gh label create --force`: `Prio:CRITICAL`,
   `Prio:WANTED`, `Prio:MINOR`, `needs-triage`.
2. Run `python3 docs/agent-guide/check_docs.py` and the strict build from
   `docs/agent-guide/testing.md`. Anything still failing belongs in the drift report.
3. Report what changed, then list every inferred reason and ask the user to confirm or correct it.
   For Actions, add that Pages' source must be set to GitHub Actions in the repo's settings.

Run again on a repo already set up, only the stub between its markers and the drift report change.
