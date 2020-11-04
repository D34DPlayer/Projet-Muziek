import sqlite3

def connect(path: str) -> sqlite3.Connection:
    return sqlite3.connect(path)

def disconnect(con: sqlite3.Connection):
    con.close()

def execute(con: sqlite3.Connection, query: str, parameters = ()):
    con.execute(query, parameters)