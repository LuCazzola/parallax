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
  If the repo is private, say this first: Pages on a private repo needs a paid plan, and the site
  is normally public anyway unless on Enterprise, so internals would be published.
- **Existing docs**, only if the repo has them. Port everything into Parallax (recommended), keep
  both side by side (existing docs stay where they are), or abort. If a public site is involved and
  the choice is to port, warn that both guides would be published with it. If the repo already
  publishes to Pages, warn that one repo has one Pages site, so side by side needs local or
  elsewhere hosting.

On abort, stop with the working tree unchanged.

For side by side, if the existing site builds from `docs/`, it will also publish `docs/parallax/`.
Name the one-line exclude its config needs, and ask to add it. It is the only change to that site.

## 3. Show the mapping

Port only. If existing docs have uncommitted changes, ask the user to commit them first, so nothing
here can lose them. Then present a table of every current page and where it goes under
`docs/parallax/pages/`, grouped by meaning, and wait for approval. Every page appears in it.

## 4. Write

Everything Parallax builds lives in `docs/parallax/`. Two things must live outside it: the workflow
in `.github/workflows/`, and the stub in `CLAUDE.md`.

1. Copy `templates/docs/parallax/` into the repo. Fill `{{site_name}}` (the existing site's name, if
   there is one), `{{repo_url}}` (drop the line if there is no remote), `{{source_root}}`. Set `ignore` in `docs/parallax/parallax.toml` to the
   generated files you found.
2. Hosting: Actions copies `templates/.github/workflows/docs.yml`, filling `{{default_branch}}`; if
   that file exists, ask for another name rather than replacing it. Local relies on
   `docs/parallax/tools/serve.py`. Elsewhere records the target and the build command in `testing.md`.
   Delete `docs/parallax/docker-compose.yml` unless the hosting is local and the repo uses Docker.
3. Python: add one `docs/parallax/pages/agent-guide/api/<package/as/path>/index.md` per package, with
   a `::: <package>` block per module, and list each in the nav. Other languages: use a generator
   if one fits, otherwise remove `mkdocstrings` and rely on the map.
4. Port by moving pages to the approved places with `git mv`, meaning unchanged. Convert other
   formats (`.rst`, `.mdx`) to Markdown, keeping every statement; a file MkDocs cannot render does
   not count as ported. A leftover config such as a root `mkdocs.yml` goes in the mapping, and is
   removed only if the user approves.
5. Fill the guides from the code, following the page comments in the templates and the writing
   rules in `parallax:sync`. Create pages only for things that exist, and delete template pages with
   nothing to say, with their nav entries. Group by meaning, and give each section an index saying
   why it exists. Remove the `<!-- parallax: -->` comments you fill. Check each statement you write
   against the code.

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
2. Run `python3 docs/parallax/tools/check_docs.py` and the strict build from
   `docs/parallax/pages/agent-guide/testing.md`. Anything still failing belongs in the drift report.
3. Report what changed, tell the user they can preview with
   `python3 docs/parallax/tools/serve.py`, then list every inferred reason and ask the user to confirm or correct it.
   For Actions, add that Pages' source must be set to GitHub Actions in the repo's settings.

Run again on a repo already set up, only the stub between its markers and the drift report change.
