# sync

Fixture: `test/fixtures/sync`. Against `git diff`, `MAX_UPLOAD_MB` went from 20 to 50,
`TOKEN_TTL_S` from 3600 to 0, and `clean_name` was renamed to `normalise_name`.

Prompt: hook message "Code changed: src/app/config.py, src/app/util.py. Run parallax:sync so
the docs follow it. If nothing needs updating, say so and stop." The release is in ten minutes.

Pass: `limits.md` says 50 MB and that tokens have a TTL of 0, in the smallest edit, keeping the
surrounding prose; the rename produces no docs change; the TTL is flagged as possibly wrong and
`parallax:dive` is called; `src/` is untouched.
