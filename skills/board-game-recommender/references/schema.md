# BGG SQLite Schema

The database is a local BoardGameGeek cache for lookup and future recommendation work. It is not a complete mirror of BGG.

## Version v0.1

Default snapshot path in this repository:

```text
releases/v0.1/bgg_games_v0.1.sqlite
```

Manifest path:

```text
releases/v0.1/manifest.json
```

v0.1 table counts:

| Table | Rows |
| --- | ---: |
| games | 2237 |
| game_links | 87685 |
| game_polls | 2237 |
| game_versions | 11658 |
| crawl_state | 4 |

## Tables

### games

One row per BGG board game.

| Column | Meaning |
| --- | --- |
| bgg_id | BGG object id. Primary key. |
| primary_name | Main game name. |
| year_published | Publication year. |
| min_players, max_players | Supported player count range. |
| min_playtime, max_playtime, playing_time | Playtime in minutes. |
| min_age | Publisher/BGG minimum age. |
| description | Plain text description extracted from BGG data. |
| image, thumbnail | BGG image URLs. |
| average | User average rating. |
| bayes_average | BGG Bayesian average rating. |
| users_rated | Number of ratings. |
| stddev, median | Rating distribution fields when available. |
| rank | BGG board game rank when available. Lower is better. |
| owned, trading, wanting, wishing | BGG collection count signals. |
| average_weight | BGG complexity/weight average, usually 1.0 to 5.0. |
| num_weights | Number of weight votes. |
| source_fetched_at | UTC timestamp for the source fetch. |
| raw_json | Original normalized JSON payload for this game. |

Useful indexes:

```sql
CREATE INDEX idx_games_rank ON games(rank);
CREATE INDEX idx_games_users_rated ON games(users_rated);
```

### game_links

Many-to-one link records for categories, mechanics, designers, artists, publishers, families, honors, versions, and other BGG link types.

| Column | Meaning |
| --- | --- |
| bgg_id | Foreign key-like reference to games.bgg_id. |
| link_type | BGG link namespace, such as boardgamecategory or boardgamemechanic. |
| link_id | BGG linked object id when available. |
| value | Human-readable linked value. |

Primary key:

```sql
PRIMARY KEY (bgg_id, link_type, value)
```

Useful index:

```sql
CREATE INDEX idx_links_type_value ON game_links(link_type, value);
```

Common `link_type` values include:

| link_type | Meaning |
| --- | --- |
| boardgamecategory | Category/theme taxonomy. |
| boardgamemechanic | Mechanic taxonomy. |
| boardgamedesigner | Designer name. |
| boardgameartist | Artist name. |
| boardgamepublisher | Publisher name. |
| boardgamefamily | Family/series/setting grouping. |
| boardgamehonor | Award or honor. |
| boardgamesubdomain | BGG subdomain such as Strategy Games. |
| boardgameversion | Named edition/version link. |

### game_versions

Edition/version records.

| Column | Meaning |
| --- | --- |
| bgg_id | Reference to games.bgg_id. |
| version_id | BGG version object id. |
| name | Version name. |
| year_published | Version publication year when available. |
| language | Version language when available. |
| publisher | Version publisher when available. |
| raw_json | Raw normalized version JSON. |

### game_polls

Poll summaries and raw poll JSON.

| Column | Meaning |
| --- | --- |
| bgg_id | Reference to games.bgg_id. |
| poll_name | Poll identifier. |
| title | Poll title. |
| total_votes | Poll vote count. |
| raw_json | Raw normalized poll JSON. |

The current crawler may store frontend poll summaries under `opencli_frontend_polls`. These can include language dependence, suggested player counts, age, and weight summaries inside `raw_json`.

### crawl_state

Crawler metadata key/value records. Use this to explain source freshness, not for game lookup.

## Query Examples

Find a game by partial name:

```sql
SELECT bgg_id, primary_name, year_published, rank, average, users_rated
FROM games
WHERE lower(primary_name) LIKE '%' || lower(:name) || '%'
ORDER BY rank IS NULL, rank, users_rated DESC
LIMIT 10;
```

Find games for a player count and time limit:

```sql
SELECT bgg_id, primary_name, min_players, max_players, playing_time, average_weight
FROM games
WHERE min_players <= :players
  AND max_players >= :players
  AND playing_time <= :max_playtime
ORDER BY rank IS NULL, rank
LIMIT 20;
```

Find games with a mechanic:

```sql
SELECT g.bgg_id, g.primary_name, g.rank, g.average
FROM games g
JOIN game_links l ON l.bgg_id = g.bgg_id
WHERE l.link_type = 'boardgamemechanic'
  AND lower(l.value) LIKE '%' || lower(:mechanic) || '%'
ORDER BY g.rank IS NULL, g.rank
LIMIT 20;
```

