# BGG Database v0.1

This directory contains the first publishable SQLite snapshot for the board game recommender skill.

Files:

- `bgg_games_v0.1.sqlite`: SQLite database snapshot.
- `manifest.json`: size, SHA-256 checksum, table counts, and crawl state metadata.

The snapshot was created from `data/bgg_games.sqlite` with the SQLite backup API so WAL data is included in a consistent database file.

