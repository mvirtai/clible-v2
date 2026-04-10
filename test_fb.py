import sqlite3

def run():
    conn = sqlite3.connect(':memory:')
    conn.execute("CREATE VIRTUAL TABLE verses_fts USING fts5(text)")
    conn.execute("INSERT INTO verses_fts(text) VALUES ('ACT 1:13 is here')")
    
    word = 'ACT 1:13'
    try:
        cursor = conn.execute("SELECT * FROM verses_fts WHERE text MATCH ?", (word,))
        print("Success!", cursor.fetchall())
    except sqlite3.OperationalError as e:
        print("Failed, fallback", e)
        safe_word = f'"{word.replace(chr(34), chr(34)+chr(34))}"'
        try:
            cursor = conn.execute("SELECT * FROM verses_fts WHERE text MATCH ?", (safe_word,))
            print("Fallback success!", cursor.fetchall())
        except sqlite3.OperationalError as e:
            print("Fallback failed", e)

run()
