# InboxSort

by Dr. Brent Allen Jensen

Organize a pile of exported `.eml` files into folders by sender and
month, and weed out the duplicates that every mailbox export seems
to grow.

Each message is parsed with the standard library's mail machinery —
headers only; bodies are never touched — and filed under
`OUT_DIR/<sender>/<YYYY-MM>/`. Duplicates are detected by Message-ID:
the second copy of a message is skipped, however it is named.

## Quickstart

```bash
python3 inboxsort.py mail-export/ sorted/
python3 inboxsort.py mail-export/ sorted/ --move
```

The run ends with a summary: how many messages were organized, how
many duplicates were skipped, and how many files could not be parsed.

## Options

| Flag | Default | Meaning |
|---|---|---|
| `--move` | off (copy) | Move files instead of copying them |

## Requirements

- Python 3.10+, standard library only

## Notes

- The sender folder comes from the From *address*, sanitized to a
  safe folder name. Messages with no parseable date land in an
  `undated` folder rather than being dropped.
- Copy is the default because exports are often the only copy. Use
  `--move` once you trust the result — or keep the export untouched
  forever; disk is cheaper than regret.

## Support this work

If this tool saved you time or taught you something, donations keep the work going:

- BTC: 15McijPo79Zx58NGyEf2PvaPtGqGmpztWn
- ETH: 0x8C25164E9234E6A30b8E44485B79c5cE8419cF2B

## License

MIT — see [LICENSE](LICENSE).
