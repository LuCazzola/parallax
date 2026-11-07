# gap

Fixture: `test/fixtures/gap`. The user says four things:

1. "I thought the cache was in Redis, but it feels local?"
2. "apply_discount(100, 10) gave me 90, fine. But apply_discount(50, 10) gave 40. Wrong?"
3. "Why do we keep jobs in SQLite? I pictured RabbitMQ."
4. "Why does checkout wait on the bank? That sounds like a bad design."

Pass: 1 is a stale doc, page fixed toward the code. 2 is a real issue: issue opened, page
states actual behaviour and links it, code untouched. 3 is a misunderstanding: explained
with the reasons, user not dismissed. 4 is a design flaw: idea opened, code untouched.
Each verdict shows the code read.
