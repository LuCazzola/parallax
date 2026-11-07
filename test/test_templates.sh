#!/usr/bin/env bash
# Fills the templates into a throwaway Python repo and runs the docs check and a real strict build.
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -r "$HERE/templates/." "$TMP/"
cd "$TMP"
rm -f CLAUDE-stub.md
find . -name __pycache__ -prune -exec rm -rf {} +
grep -rlE '\{\{(site_name|repo_url|source_root|default_branch)\}\}' . | xargs sed -i \
  -e 's/{{default_branch}}/trunk/g' -e 's/{{site_name}}/Fixture/g' -e 's#{{repo_url}}#https://github.com/o/fixture#g' -e 's/{{source_root}}/src/g'
D=docs/parallax; PG=$D/pages
mkdir -p src/fixture $PG/agent-guide/api/fixture docs/parallax/notes
printf '"""Fixture."""\n' > src/fixture/__init__.py
printf 'def run() -> int:\n    """Run."""\n    return 1\n' > src/fixture/core.py
printf '::: fixture\n\n::: fixture.core\n' > $PG/agent-guide/api/fixture/index.md
printf '# Note\n' > $D/notes/note.md
cat > $PG/user-guide/core.md <<'P'
# Core

Code: `src/fixture/core.py`

```mermaid
classDiagram
    class Run
    cssClass "Run" impl
```
P
sed -i 's#      - user-guide/index.md#      - user-guide/index.md\n      - Core: user-guide/core.md#' $D/mkdocs.yml
sed -i 's#      - Glossary: agent-guide/glossary.md#      - Glossary: agent-guide/glossary.md\n      - API: agent-guide/api/fixture/index.md#' $D/mkdocs.yml
python3 $D/tools/check_docs.py
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e NO_MKDOCS_2_WARNING=1 -v "$TMP:/repo" -w /repo \
  ghcr.io/astral-sh/uv:0.9.30-python3.12-bookworm-slim \
  uvx --with-requirements docs/parallax/requirements.txt mkdocs build --strict -f docs/parallax/mkdocs.yml -d /repo/site
test -f site/agent-guide/index.html
test -f site/agent-guide/api/fixture/index.html
test ! -e site/notes
test ! -e site/tools
test -z "$(find . -maxdepth 1 -type f)"
test "$(ls -A | LC_ALL=C sort | tr '\n' ' ')" = ".github docs site src "
grep -q 'stylesheets/extra.css' site/index.html
grep -q 'javascripts/mermaid.js' site/index.html
grep -q 'mermaid-diagram' site/user-guide/core/index.html
grep -q 'cssClass' site/user-guide/core/index.html
grep -q 'branches: \[trunk\]' .github/workflows/docs.yml
grep -q 'pull_request' .github/workflows/docs.yml
python3 - <<'P'
import tomllib, sys
cfg = tomllib.load(open("docs/parallax/parallax.toml", "rb"))
assert cfg["tickets"]["auto_file_issues"] == "private"
P
echo "templates ok"
