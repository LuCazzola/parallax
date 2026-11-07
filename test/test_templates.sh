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
mkdir -p src/fixture docs/agent-guide/api/fixture docs/investigations
printf '"""Fixture."""\n' > src/fixture/__init__.py
printf 'def run() -> int:\n    """Run."""\n    return 1\n' > src/fixture/core.py
printf '::: fixture\n\n::: fixture.core\n' > docs/agent-guide/api/fixture/index.md
printf '# Note\n' > docs/investigations/note.md
cat > docs/user-guide/core.md <<'P'
# Core

Code: `src/fixture/core.py`

```mermaid
classDiagram
    class Run
    cssClass "Run" impl
```
P
sed -i 's#      - user-guide/index.md#      - user-guide/index.md\n      - Core: user-guide/core.md#' mkdocs.yml
sed -i 's#      - Glossary: agent-guide/glossary.md#      - Glossary: agent-guide/glossary.md\n      - API: agent-guide/api/fixture/index.md#' mkdocs.yml
python3 docs/agent-guide/check_docs.py
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e NO_MKDOCS_2_WARNING=1 -v "$TMP:/repo" -w /repo \
  ghcr.io/astral-sh/uv:0.9.30-python3.12-bookworm-slim \
  uvx --with mkdocs-material==9.7.7 --with mkdocstrings==1.0.6 --with mkdocstrings-python==2.0.9 \
  --with griffe==2.3.0 --with mkdocs-autorefs==1.4.4 --with pymdown-extensions==11.0.2 \
  mkdocs==1.6.1 build --strict -d site
test -f site/agent-guide/index.html
test -f site/agent-guide/api/fixture/index.html
test ! -e site/investigations
test ! -e site/agent-guide/check_docs.py
grep -q 'stylesheets/extra.css' site/index.html
grep -q 'javascripts/mermaid.js' site/index.html
grep -q 'mermaid-diagram' site/user-guide/core/index.html
grep -q 'cssClass' site/user-guide/core/index.html
grep -q 'branches: \[trunk\]' .github/workflows/docs.yml
grep -q 'pull_request' .github/workflows/docs.yml
python3 - <<'P'
import tomllib, sys
cfg = tomllib.load(open(".parallax.toml", "rb"))
assert cfg["tickets"]["auto_file_issues"] == "private"
P
echo "templates ok"
