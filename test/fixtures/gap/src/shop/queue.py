import sqlite3


def enqueue(db: sqlite3.Connection, job: str) -> None:
    db.execute("insert into jobs(name) values (?)", (job,))
