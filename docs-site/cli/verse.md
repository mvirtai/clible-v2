# `clible verse`

Look up a single verse or a verse range.

```bash
clible verse "John 3:16"
clible verse "John 3:16-18"
clible verse "Genesis 1:1" -t kjv
clible verse "John 3:16" --all
clible verse "John 3:16" --language es
```

`--all` displays a verse or verse range from every translation already seeded
on this machine. `--language CODE` limits that multi-translation view to a
language code such as `es`; it also works without `--all`. Neither option
downloads translations or can be combined with `-t` or export options.

