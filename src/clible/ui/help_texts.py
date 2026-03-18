"""Centralized help text constants for CLI commands."""

# Note: Using ''' for docstrings and """ for multiline f-strings or other text.
# This helps avoid escaping issues with rich markup.

# --- Analytics Commands --- #

ANALYTICS_REFERENCE_HELP = """
[bold]Usage: clible analytics reference [REF] [OPTIONS][/bold]

  Analyzes a specific biblical reference for word statistics.

  This command calculates metrics like token count and type-token ratio,
  and identifies the most frequent words and n-grams (bigrams, trigrams)
  within the specified verse or range of verses.

[bold]Arguments:[/bold]
  [REF]  The biblical reference to analyze (e.g., "John 3:16", "Gen 1:1-5").
         This argument is required.

[bold]Options:[/bold]
  -t, --translation TEXT  Translation ID (e.g., 'web'). Defaults to the
                          primary installed translation.
  -n, --top INTEGER       Number of top items to show for words and n-grams.
                          [default: 10]
  --output PATH           Write results to a file. Format is inferred from
                          extension: .json/.csv/.html/.md
  --help                  Show this message and exit.

[bold]Examples:[/bold]
  1. Analyze a single verse with the default translation:
     [cyan]clible analytics reference "John 3:16"[/cyan]

  2. Analyze a range of verses in the KJV and show the top 5 items:
     [cyan]clible analytics reference "Genesis 1:1-5" -t kjv --top 5[/cyan]
"""

ANALYTICS_CHAPTER_HELP = """
[bold]Usage: clible analytics chapter [BOOK] [CHAPTER] [OPTIONS][/bold]

  Analyzes all verses in a chapter for word statistics.

  This command aggregates text from an entire chapter and performs a
  statistical analysis, including token counts, vocabulary richness
  (type-token ratio), and top n-grams.

[bold]Arguments:[/bold]
  [BOOK]     The name of the book (e.g., "John", "Genesis").
  [CHAPTER]  The chapter number.

[bold]Options:[/bold]
  -t, --translation TEXT  Translation ID (e.g., 'web'). Defaults to the
                          primary installed translation.
  -n, --top INTEGER       Number of top items to show for words and n-grams.
                          [default: 10]
  --output PATH           Write results to a file. Format is inferred from
                          extension: .json/.csv/.html/.md
  --help                  Show this message and exit.

[bold]Examples:[/bold]
  1. Analyze chapter 3 of John with the default translation:
     [cyan]clible analytics chapter John 3[/cyan]

  2. Analyze chapter 1 of Genesis in the KJV and show the top 5 items:
     [cyan]clible analytics chapter Genesis 1 -t kjv --top 5[/cyan]
"""

ANALYTICS_BOOK_HELP = """
[bold]Usage: clible analytics book [BOOK] [OPTIONS][/bold]

  Analyzes all verses in a book for word statistics.

  This command aggregates text from an entire book to provide high-level
  textual analysis, including token counts, vocabulary richness, and the
  most frequent words and n-grams across the entire book.

[bold]Arguments:[/bold]
  [BOOK]  The name of the book to analyze (e.g., "John", "Genesis").

[bold]Options:[/bold]
  -t, --translation TEXT  Translation ID (e.g., 'web'). Defaults to the
                          primary installed translation.
  -n, --top INTEGER       Number of top items to show for words and n-grams.
                          [default: 10]
  --output PATH           Write results to a file. Format is inferred from
                          extension: .json/.csv/.html/.md
  --help                  Show this message and exit.

[bold]Examples:[/bold]
  1. Analyze the book of John with the default translation:
     [cyan]clible analytics book John[/cyan]

  2. Analyze the book of Genesis in the KJV and show the top 15 items:
     [cyan]clible analytics book Genesis -t kjv --top 15[/cyan]
"""

ANALYTICS_COMPARE_HELP = """
[bold]Usage: clible analytics compare [REF] [OPTIONS][/bold]

  Compares two translations side-by-side for a given biblical reference.
  This command provides a verse-by-verse view with word-level diffs and
  calculates text similarity scores.

[bold]Arguments:[/bold]
  [REF]  The biblical reference to analyze (e.g., "John 3", "Gen 1:1-5").
         This argument is required.

[bold]Options:[/bold]
  --left TEXT    The base translation for comparison.
                 [default: fin-1992]

  --right TEXT   The translation to compare against the base.
                 [default: fin17xx (alias for fin-1776)]

  --output PATH  Write results to a file. Format is inferred from extension:
                 .json/.csv/.html/.md
  --help         Show this message and exit.

[bold]Examples:[/bold]
  1. Compare Psalm 23 using the default Finnish translations:
     [cyan]clible analytics compare "Psalm 23"[/cyan]

  2. Compare the entire book of Genesis between KJV and WEB:
     [cyan]clible analytics compare "Genesis" --left kjv --right web[/cyan]
"""

# --- Seed Commands --- #

SEED_INSTALL_HELP = """
[bold]Usage: clible seed install [TRANSLATION_ID] [OPTIONS][/bold]

  Downloads, parses, and installs a single Bible translation.

  The command fetches the source data (typically XML), processes it into a
  standard format, and saves the verses to the local database.

[bold]Arguments:[/bold]
  [TRANSLATION_ID]  Translation ID to install.
                   To see a list of available IDs, run `clible seed available`.

[bold]Options:[/bold]
  --help  Show this message and exit.

[bold]Examples:[/bold]
  1. Install the World English Bible:
     [cyan]clible seed install web[/cyan]
"""

SEED_AVAILABLE_HELP = """
[bold]Usage: clible seed available [OPTIONS][/bold]

  Lists all Bible translations available for installation from the catalog.

  This command reads the official data catalog and displays a table of
  translation IDs, names, and source formats (e.g., OSIS, USFX).

[bold]Options:[/bold]
  --help  Show this message and exit.
"""

SEED_LIST_HELP = """
[bold]Usage: clible seed list [OPTIONS][/bold]

  Lists all Bible translations that are currently installed locally.

[bold]Options:[/bold]
  --help  Show this message and exit.
"""

SEED_REMOVE_HELP = """
[bold]Usage: clible seed remove [TRANSLATION_ID] [OPTIONS][/bold]

  Uninstalls an installed Bible translation and deletes its data.

[bold]Arguments:[/bold]
  [TRANSLATION_ID]  Translation ID to remove.

[bold]Options:[/bold]
  --help  Show this message and exit.

[bold]Examples:[/bold]
  1. Remove the World English Bible:
     [cyan]clible seed remove web[/cyan]
"""

# --- Verse, Search, and Backup Commands --- #

VERSE_HELP = """
[bold]Usage: clible verse [REFERENCE] [OPTIONS][/bold]

  Displays the text of a specific Bible verse or a range of verses.

[bold]Arguments:[/bold]
  [REFERENCE]  The biblical reference to look up.
               Examples: "John 3:16", "John 3:1-6", "Genesis 1:1-5".

[bold]Options:[/bold]
  -t, --translation TEXT  Translation ID (e.g. 'web'). Defaults to the
                          primary installed translation.
  --help                  Show this message and exit.

[bold]Examples:[/bold]
  1. Look up a single verse in the primary translation:
     [cyan]clible verse "John 3:16"[/cyan]

  2. Look up a range of verses:
     [cyan]clible verse "Genesis 1:1-5"[/cyan]

  3. Look up a verse in a specific translation (KJV):
     [cyan]clible verse "John 3:16" -t kjv[/cyan]
"""

SEARCH_HELP = """
[bold]Usage: clible search [QUERY] [OPTIONS][/bold]

  Performs a full-text search across the entire Bible or a defined scope.

  This command uses an FTS5 index for fast and powerful searching. It returns
  a statistical summary and a list of matching verses.

[bold]Arguments:[/bold]
  [QUERY]  The word or phrase to search for.

[bold]Options:[/bold]
  -s, --scope [verse|chapter|book|testament|bible]
                                  The scope to search within.
                                  [default: bible]
  -r, --reference TEXT            The reference for the chosen scope (e.g.,
                                  "NT" for testament, "John" for book, "Hebrews
                                  11" for chapter).
  -t, --translation TEXT          The translation to search in. Defaults to
                                  the primary translation.
  -n, --limit INTEGER             Maximum number of verses to display.
  --help                          Show this message and exit.

[bold]Examples:[/bold]
  1. Search for 'grace' across the entire Bible:
     [cyan]clible search grace[/cyan]

  2. Search for 'love' within the book of John in the WEB translation:
     [cyan]clible search love -s book -r John -t web[/cyan]

  3. Search for 'faith' in the New Testament and limit results to 5:
     [cyan]clible search faith -s testament -r NT -n 5[/cyan]
"""

BACKUP_HELP = """
[bold]Usage: clible backup [OPTIONS][/bold]

  Manages backups of the local SQLite database.

  This command currently supports uploading the database to a Google Cloud
  Storage (GCS) bucket. The bucket must be specified via the
  `CLIBLE_GCS_BUCKET` environment variable.

[bold]Options:[/bold]
  --help  Show this message and exit.

[bold]Example:[/bold]
  (Assuming CLIBLE_GCS_BUCKET is set)
  [cyan]clible backup[/cyan]
"""

BACKUP_GCS_HELP = """
[bold]Usage: clible backup gcs [OPTIONS][/bold]

  Upload the local SQLite database to Google Cloud Storage (GCS).

  Requires the `CLIBLE_GCS_BUCKET` environment variable.

[bold]Options:[/bold]
  --help  Show this message and exit.
"""

BACKUP_RESTORE_GCS_HELP = """
[bold]Usage: clible backup restore-gcs [GCS_URI] [OPTIONS][/bold]

  Restore the local SQLite database from a GCS object.

  The command downloads the remote database into a temporary file,
  backs up the currently configured local DB (if it exists),
  and then replaces it with the downloaded one.

[bold]Arguments:[/bold]
  [GCS_URI]  GCS URI of the backup database (e.g. "gs://bucket/path/file.db").

[bold]Options:[/bold]
  --force  Skip the confirmation prompt before replacing the local database.
  --help   Show this message and exit.

[bold]Example:[/bold]
  [cyan]clible backup restore-gcs gs://my-bucket/backups/clible.db --force[/cyan]
"""
