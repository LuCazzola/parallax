# Testing

<!-- parallax: how to run this repo's tests. -->

## Docs checks

```bash
python3 docs/parallax/tools/check_docs.py
```

This checks that the paths docs name exist, that each User Guide page has a `Code:` line,
and that API stubs match the packages. A pass means they match, not that what they say
is right.

The site must also build with `--strict`:

```bash
python3 docs/parallax/tools/serve.py --build
```

## Preview the site

```bash
python3 docs/parallax/tools/serve.py
```

Then open <http://127.0.0.1:8000>. It reloads as pages change. It needs only Python: the first run
without `uv` sets up the tools in a private folder, ignored by git. Versions are pinned in
`docs/parallax/requirements.txt`, the one place to change them.
