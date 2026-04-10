import sqlite3


def run():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE VIRTUAL TABLE verses_fts USING fts5(text, book_id UNINDEXED, chapter UNINDEXED, verse UNINDEXED)"
    )

    # insert dummy
    conn.execute("INSERT INTO verses_fts(text) VALUES ('ACT 1:13 it was good')")

    for word in ["ACT 1:13", "ACT", "1:13", '"ACT"', "grace AND truth", "foo:bar"]:
        escaped_word = f'"{word.replace(chr(34), chr(34) + chr(34))}"'
        try:
            cursor = conn.execute("SELECT * FROM verses_fts WHERE text MATCH ?", (escaped_word,))
            print(f"Success escaped {word!r}: {len(cursor.fetchall())} results")
        except Exception as e:
            print(f"Error for escaped {word!r}:", type(e), e)


run()
