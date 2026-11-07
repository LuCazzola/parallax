import sqlite3


def save(db: sqlite3.Connection, celsius: float) -> None:
    db.execute("insert into readings(celsius) values (?)", (celsius,))
