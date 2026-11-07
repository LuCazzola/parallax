#!/usr/bin/env python3
"""Checks docs against the repo with no model in the loop: paths named in docs exist, User
Guide pages name their code, API stubs match the packages. A pass means paths match, not that
what the docs say is right."""
import re
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKIP_DIRS = {"investigations", "superpowers"}
NOT_A_PATH = re.compile(r"[\s<>*{}$]|://")
EXTENSION = re.compile(r"\.[A-Za-z][A-Za-z0-9]*$")
CODE_LINE = re.compile(r"^Code:\s")
INLINE = re.compile(r"`([^`\n]+)`")


def load_config():
    try:
        with (REPO / ".parallax.toml").open("rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError) as e:
        sys.exit(print(f".parallax.toml: cannot read it: {e}") or 1)


def looks_like_path(token):
    """Only a token rooted at an existing top-level entry counts: `nowhere/b` is prose."""
    if NOT_A_PATH.search(token) or token.startswith(("/", "..", "~")):
        return False
    if "/" not in token and not EXTENSION.search(token):
        return False
    return (REPO / token.removeprefix("./").split("/")[0]).exists()


def page_lines(page):
    fenced = False
    for number, line in enumerate(page.read_text().splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            yield number, line


def check_page(page, rel, require_code_line):
    problems, has_code_line = [], False
    for number, line in page_lines(page):
        is_code_line = bool(CODE_LINE.match(line))
        has_code_line |= is_code_line
        for token in INLINE.findall(line):
            if (is_code_line or looks_like_path(token)) and not (REPO / token).exists():
                problems.append(f"{rel}:{number}: missing path {token}")
    if require_code_line and not has_code_line:
        problems.append(f"{rel}:1: User Guide page has no Code: line")
    return problems


def packages(root):
    return {".".join(p.parent.relative_to(root).parts): p.parent for p in root.rglob("__init__.py")}


def check_api_stubs(docs, cfg):
    api = docs / "agent-guide" / "api"
    if not api.is_dir():
        return []
    problems, found = [], {}
    for source in cfg.get("source_roots", []):
        found.update({name: (path, api / path.relative_to(REPO / source) / "index.md")
                      for name, path in packages(REPO / source).items()})
    for name, (path, stub) in found.items():
        if not stub.is_file():
            problems.append(f"{stub.relative_to(REPO)}: missing API stub for {name}")
            continue
        text = stub.read_text()
        wanted = [name] + [f"{name}.{m.stem}" for m in path.glob("*.py") if m.name != "__init__.py"]
        problems += [f"{stub.relative_to(REPO)}: stub skips {w}" for w in wanted if f"::: {w}\n" not in text]
    stubs = {stub for _, stub in found.values()}
    nav = (REPO / "mkdocs.yml").read_text()
    for stub in api.rglob("*.md"):
        rel = stub.relative_to(docs)
        if stub not in stubs:
            problems.append(f"{rel}: stub for a package that no longer exists")
        if str(rel) not in nav:
            problems.append(f"{rel}: not in the mkdocs nav")
    return problems


def main():
    cfg = load_config()
    docs = REPO / cfg.get("docs_dir", "docs")
    guide = docs / "user-guide"
    problems = []
    for page in sorted(docs.rglob("*.md")):
        if SKIP_DIRS & set(page.relative_to(docs).parts):
            continue
        rel = page.relative_to(REPO)
        problems += check_page(page, rel, page.parent == guide and page.name != "index.md")
    problems += check_api_stubs(docs, cfg)
    print("\n".join(problems) or "docs check passed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
