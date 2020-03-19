import sqlite3


conn = sqlite3.connect('resumedb.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Resume')

conn.commit()
