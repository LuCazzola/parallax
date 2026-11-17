# user-guide

Two runs, both with only `parallax:setup` and `parallax:sync` as writing instructions.

**Whole guide.** Fixture: this repo, with `templates/docs/parallax/` imagined as copied to
`docs/parallax/`. Prompt: carry out step 4.5 of `parallax:setup` for the User Guide only.

Pass: the index draws the whole system in one diagram and gives a reading order with its
reason; the nav follows that order; every page that describes steps, branches, states or parts
has a picture; every page opens by picking up from the page before it and closes with a link
to the next one and the question it answers. Detail survives the shape: the page on
`hooks/check_sync.py` states, each with its value or condition, that a commit followed by a
checkout in one turn is not reported, that a session idle past `STALE_S` reports nothing for its
next turn, and that a failing hook looks the same as a turn with no changes.

**New page in an existing guide.** Fixture: a repo whose User Guide has sections and one
subsystem with no page. Prompt: step 4 of `parallax:sync` for that subsystem.

Pass: the page sits inside the chapter it belongs to, with the sections kept; it has the five
parts; the pages on either side have their opening and closing lines rewritten to include it;
no other prose changes. A picture of a value over time is an inline SVG with
`class="parallax-fig"`, an `aria-label`, and no path sampled point by point.

Baseline without the "Writing the User Guide" section: one diagram in a guide of 13 to 16
pages, and no page says where it sits or where to go next.
