# Parallax

Docs for two readers, humans and agents, that always follow the code.

Parallax is the shift you see when two viewpoints look at one object. In a codebase, the two
viewpoints are your picture of the system and what the system does. When they disagree, that is
worth knowing: it might be a stale page, a real bug, a design flaw, or a misunderstanding.
Parallax is a Claude Code plugin that makes those gaps visible and gives each one somewhere to go.

## The hard rule

**The code is the oracle, docs follow, and neither implies correctness.**

- When docs and code disagree, the page changes. No skill ever changes code to match a doc.
- If the code is buggy, the docs describe the buggy behaviour. A strange behaviour written in
  plain words is easier to question.
- Docs are leads. Agents check a claim in the code before relying on it.

## Install

```text
/plugin install parallax --marketplace LuCazzola/parallax
```

If that form isn't available yet, use the two-step install:

```text
/plugin marketplace add LuCazzola/parallax
/plugin install parallax@parallax
```

The automatic hook was tested on Claude Code 2.1.319.

Then, in the repo you want to document:

```text
/parallax:setup
```

## What you get

Your repo's docs split by who reads them:

| Guide | For | Holds |
|---|---|---|
| **User Guide** | People supervising the system | Design decisions and their consequences, so you can check them against your own picture |
| **Agent Guide** | Agents doing the work | Code map, recipes, testing, generated API reference, tickets |

Plus an MkDocs Material site with a dark mode and colour-coded, zoomable diagrams, a docs check
that needs no AI, and ticket scripts that work without the plugin.

## The skills

| Skill | Runs | Does |
|---|---|---|
| `parallax:setup` | Once, by you | Builds the docs, or ports yours after showing you the mapping. Asks where to host them |
| `parallax:sync` | Automatically after code changes | Moves pages to what the code does now, with the smallest edit |
| `parallax:dive` | When sync doubts something, or when you ask | Sends a read-only skeptic to ask whether what docs and code agree on looks like a bug. Also the whole-repo health check |
| `parallax:gap` | When your picture differs from the docs | Reads the code and decides: stale doc, real issue, design flaw, or misunderstanding |
| `parallax:ticket` | When something should be kept for later | Files an idea in the repo, or a GitHub issue. Asks first on public repos |

`sync` fires through a hook: when an agent finishes a turn in which code changed, it is sent to
sync once per change. Every skill except `setup` applies only to repos with a `.parallax.toml`, so
othing changes anywhere else.

## What setup changes in your repo

- `docs/`, split into `user-guide/` and `agent-guide/`
- `mkdocs.yml`, `.parallax.toml`
- A short block in `CLAUDE.md`, between `parallax` markers, so agents without the plugin get the rule
- A publishing workflow or Docker setup, depending on what you choose
- GitHub labels for tickets

Reasons the agent inferred are marked "Inferred, not confirmed" until you confirm them.

## Hosting

Setup asks. GitHub Actions is recommended; local (`docker compose -f docker-compose.docs.yml up`, or
`uvx`) and your own host also work.
On a private repo, Pages needs a paid plan, and the site is normally public unless you are on
Enterprise, so setup warns you first.

## Requirements

- Claude Code
- Python 3.11+ and `git` (below 3.11 the hook stays silent and the checks don't run)
- `gh` for GitHub issues (without it you get the ideas table)
- `uv` or Docker to build the site locally

API reference generation is Python first; other languages are best effort.

## Development

```bash
python3 -m unittest discover -s test
bash test/test_templates.sh          # needs Docker
```

`test/scenarios/` holds the pressure scenarios used to prove each skill against a baseline.

## License

MIT
