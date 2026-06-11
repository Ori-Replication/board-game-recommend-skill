---
name: board-game-recommender
description: Recommend suitable board games for users using a local BoardGameGeek SQLite cache plus conversational context. Use when Codex needs to recommend board games, compare candidate games, answer board game fit questions, inspect BGG metadata, or query ratings, ranks, player counts, playtime, weight, categories, mechanics, designers, publishers, versions, and poll data from the bundled/local database.
---

# Board Game Recommender

Use this skill to recommend board games and query a local BoardGameGeek SQLite cache. Prefer practical fit over raw BGG rank.

## Data Source

Default database lookup order:

1. Use `BGG_DB_PATH` when it is set.
2. Use a user-provided database path when the user gives one.
3. Look for `releases/v0.1/bgg_games_v0.1.sqlite` from the current project root.
4. Look for `data/bgg_games.sqlite` from the current project root.

The v0.1 snapshot is a SQLite database generated from the crawler output. It focuses on BGG games with average rating above 6.0 and enough rating volume to be useful. This creates a quality-oriented but BGG-biased dataset; it may underrepresent local hits, children's games, party games, newer games, and games popular mainly outside BGG.

Read `references/schema.md` when you need field definitions, table relationships, or query examples. Read `references/recommendation-policy.md` when the user asks for recommendations or game fit judgments.

## Recommendation Workflow

1. Use conversation context to infer obvious constraints, but avoid stereotypes. Treat age, location, language, experience, group type, and play setting as useful; do not overuse gender or profession.
2. If key constraints are missing, ask a small number of questions before recommending. Prioritize exact player count, country/region and language access, play setting, experience level, desired duration, and complexity tolerance.
3. Query the database for candidates that fit hard constraints such as player count, time, weight, and desired categories/mechanics.
4. If the user's preference is strong but the local database has weak coverage, use external search or general board game knowledge to add out-of-database candidates. Label these clearly.
5. Adjust using practical access: local availability, club/store play, language dependence, online play, rules/tutorial resources, and whether the user needs to buy the game or only play it.
6. Present a short, reasoned shortlist. Explain why each game fits, what conditions it needs, and any uncertainty.

## Query Workflow

1. Identify whether the user asks for game records, schema details, link values, versions, or poll data.
2. Read `references/schema.md` for table and field details if needed.
3. Use `scripts/query_bgg_db.py` for deterministic database lookup.
4. Return factual database results with the database version/path when useful.
5. Mention data gaps clearly when fields are null or records are absent.

## Script Usage

Search games by name:

```bash
python scripts/query_bgg_db.py search --name "gloomhaven" --limit 5
```

Inspect one game with joined links, versions, and polls:

```bash
python scripts/query_bgg_db.py game --id 174430
```

Filter games:

```bash
python scripts/query_bgg_db.py search --players 4 --max-playtime 120 --min-rating 7 --max-weight 3.5 --limit 20
```

List common link values such as categories or mechanics:

```bash
python scripts/query_bgg_db.py links --type boardgamemechanic --limit 30
```

Print schema metadata:

```bash
python scripts/query_bgg_db.py schema
```
