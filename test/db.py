import sqlite3

conn = sqlite3.connect('test.sqlite')

cursor = conn.cursor()

query = """CREATE TABLE test (
    id integer PRIMARY KEY,
    author text NOT NULL,
    language text NOT NULL,
    title text NOT NULL    
)"""

cursor.execute(query)