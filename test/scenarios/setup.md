# setup

Fixture: `test/fixtures/setup-existing`, an existing private repo with stale docs (Postgres vs
SQLite, a missing `registry.py`) and doc rules in `CLAUDE.md`.

Prompt: set up Parallax; answers supplied up front are GitHub Actions and port everything.

Pass: hosting question asked with Actions recommended and the private-repo warning shown; port,
side-by-side and abort offered; mapping shown before moving; existing content kept with meaning
unchanged; the Postgres and `registry.py` mismatches flagged, not silently fixed; inferred reasons
marked and listed for confirmation, and the person-written reason kept as confirmed unless the code
contradicts it; only the marked stub added to `CLAUDE.md`, and replacing its doc rule proposed;
`check_docs.py` green apart from flagged items; no code changed.

Second run: same fixture, answer abort. Pass: `git status` clean.
Third run: re-run on the result. Pass: nothing changes outside the markers.

Collisions: the fixture has its own `docs/index.md` and `mkdocs.yml`. Pass: both appear in the
mapping, their content survives in the result, and the site name stays "Weather handbook".

Side by side: same fixture, hosting local. Pass: `git status` shows only `CLAUDE.md` and
`docs/parallax/`, plus the exclude in the existing `mkdocs.yml` if approved, which is asked for first.
