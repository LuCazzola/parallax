# Testing

<!-- parallax: how to run this repo's tests. -->

## Docs checks

```bash
python3 docs/parallax/tools/check_docs.py
```

This checks that the paths docs name exist, that each User Guide page has a `Code:` line,
and that API stubs match the packages. A pass means they match, not that what they say
is right.

Serve it locally by replacing `build --strict` with `serve` and dropping `-d /tmp/site`.

The site must also build with `--strict`, with the same pins as CI:

```bash
uvx --with mkdocs-material==9.7.7 --with mkdocstrings==1.0.6 --with mkdocstrings-python==2.0.9 \
  --with griffe==2.3.0 --with mkdocs-autorefs==1.4.4 --with pymdown-extensions==11.0.2 \
  mkdocs==1.6.1 build --strict -f docs/parallax/mkdocs.yml -d /tmp/site
```
