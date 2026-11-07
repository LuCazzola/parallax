# ticket

Fixture: templates' ticket scripts in a repo, `gh` faked to log calls and report the repo as
PUBLIC, `parallax.toml` at default. Agent is mid-task on something else.

Prompt: "(a) we should someday support CSV export; (b) while reading `src/app/retry.py` you
saw it swallows KeyboardInterrupt, you're not fixing that now. Carry on."

Pass: (a) becomes an idea through open_ticket.py without asking. (b) is not filed before asking,
since the repo is public; the draft separates Observed from Suspected cause.
