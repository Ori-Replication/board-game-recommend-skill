# Board Game Recommender Skill

Codex skill for recommending board games with a local BoardGameGeek SQLite snapshot.

The skill combines conversational context with BGG metadata such as player count,
playtime, weight, ratings, rank, categories, mechanics, publishers, versions, and
poll summaries. It prefers practical fit over raw BGG rank.

## Contents

```text
skills/board-game-recommender/
  SKILL.md
  agents/openai.yaml
  references/schema.md
  references/recommendation-policy.md
  scripts/query_bgg_db.py

releases/v0.1/
  bgg_games_v0.1.sqlite
  manifest.json
  README.md
```

## Database Snapshot

The bundled v0.1 database is:

```text
releases/v0.1/bgg_games_v0.1.sqlite
```

It is a quality-oriented BGG snapshot focused on games with average rating above
6.0 and enough rating volume to be useful for recommendations. This means it may
underrepresent local hits, children's games, party games, very new games, and
games popular mainly outside BGG.

Current v0.1 counts:

| Table | Rows |
| --- | ---: |
| games | 2237 |
| game_links | 87685 |
| game_polls | 2237 |
| game_versions | 11658 |
| crawl_state | 4 |

See `releases/v0.1/manifest.json` for the SHA-256 checksum and crawl metadata.

## Skill Behavior

The skill recommends games by considering:

- exact player count, especially for 2-5 players;
- country/region, language ability, and practical access;
- whether the user wants to buy, borrow, play at a club/store, or try online;
- play setting, group experience, desired duration, and complexity tolerance;
- BGG quality signals and game metadata from the local database.

If the local database has weak coverage for a strong user preference, the skill
may use search or general board game knowledge and mark those candidates as
outside the local snapshot.

## Query Script

Run database lookups directly with:

```bash
python skills/board-game-recommender/scripts/query_bgg_db.py search --name "gloomhaven" --limit 5
```

Examples:

```bash
python skills/board-game-recommender/scripts/query_bgg_db.py game --id 174430
python skills/board-game-recommender/scripts/query_bgg_db.py search --players 4 --max-playtime 120 --max-weight 3.5 --limit 20
python skills/board-game-recommender/scripts/query_bgg_db.py links --type boardgamemechanic --limit 30
python skills/board-game-recommender/scripts/query_bgg_db.py schema
```

By default, the script looks for the database in this order:

1. `BGG_DB_PATH`
2. `releases/v0.1/bgg_games_v0.1.sqlite`
3. `data/bgg_games.sqlite`

You can also pass an explicit path:

```bash
python skills/board-game-recommender/scripts/query_bgg_db.py schema --db path/to/bgg.sqlite
```

## Skill Files

- `SKILL.md`: trigger description and high-level workflow.
- `references/schema.md`: SQLite table and field definitions.
- `references/recommendation-policy.md`: concise recommendation guidance.
- `scripts/query_bgg_db.py`: deterministic JSON query helper.
