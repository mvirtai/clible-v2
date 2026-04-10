import sqlite3

def run():
    conn = sqlite3.connect(':memory:')
    conn.execute("CREATE VIRTUAL TABLE verses_fts USING fts5(text, book_id UNINDEXED, chapter UNINDEXED, verse UNINDEXED)")
    try:
        conn.execute("SELECT * FROM verses_fts WHERE text MATCH ?", ('"ACT 1:13"',))
        print("Success for phrase")
    except Exception as e:
        print("Error for phrase:", type(e), e)

    try:
        conn.execute("SELECT * FROM verses_fts WHERE text MATCH ?", ('ACT 1:13',))
        print("Success for simple")
    except Exception as e:
        print("Error for simple:", type(e), e)

run()
