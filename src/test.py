import sqlite3
from db_interface import *
conn = sqlite3.connect("bilinkedin.db")
cur = conn.cursor()

rows = cur.execute("SELECT * from Customer;")
for row in rows:
    print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

rows = cur.execute("SELECT * from Professional;")
for row in rows:
    print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

rows = cur.execute("SELECT * from ActiveUsers;")
for row in rows:
    print(row[0], row[1])

check_professional('ali')

for row in rows:
    print(row)


rows = cur.execute("SELECT * FROM;")
for row in rows:
    print(row)
