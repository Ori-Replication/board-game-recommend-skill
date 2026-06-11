# Board Game Recommender Data Crawler

This repository contains a local BoardGameGeek crawler for building a SQLite
cache suitable for recommendation.

The crawler intentionally uses BGG's official XML API and official rank CSV
instead of scraping HTML pages. BGG currently requires an approved application
token for XML API access. The rank CSV may also require a fresh browser cookie
when Cloudflare challenges automated downloads.

## Rating Threshold

The default crawl thresholds are:

- `usersrated >= 75` for normal games.
- `usersrated >= 30` for games published in the current year or previous two years.

This keeps the dataset focused on games with enough public signal for
recommendation while still letting newer games enter the index before they have
hundreds of ratings.

## Usage

Set your BGG token:

```powershell
$env:BGG_TOKEN = "your-token"
```

Optionally set a fresh BGG browser cookie for downloading rank CSV data:

```powershell
$env:BGG_COOKIE = "cf_clearance=..."
```

Download the official rank CSV:

```powershell
python .\bgg_crawler.py fetch-ranks --output data\bg_ranks.csv
```

If the official rank CSV returns a site shell or Cloudflare page, build a
candidate CSV from BGG browse pages instead:

```powershell
python .\bgg_crawler.py fetch-browse --max-pages 200 --output data\bgg_browse_candidates.csv
```

Smoke-test one game:

```powershell
python .\bgg_crawler.py smoke-test --id 174430
```

Crawl detailed data with the default 75/30 rating thresholds:

```powershell
python .\bgg_crawler.py crawl --ranks-csv data\bg_ranks.csv --db data\bgg_games.sqlite --resume
```

Or crawl from the browse candidate CSV:

```powershell
python .\bgg_crawler.py crawl --ranks-csv data\bgg_browse_candidates.csv --db data\bgg_games.sqlite --resume
```

If you do not have a BGG XML API token, the best fallback is browser-context
fetching. It opens BGG once through OpenCLI, then uses the browser page itself
to `fetch()` detail HTML and extract `GEEK.geekitemPreload` without navigating
for every game:

```powershell
opencli daemon restart
opencli daemon status
python .\bgg_crawler.py crawl-browser-fetch --ranks-csv data\bgg_browse_candidates.csv --db data\bgg_games.sqlite --resume --batch-size 20 --fetch-concurrency 2 --fetch-delay 1
```

This is much lighter than page-by-page browser navigation, while still using
the connected browser context when direct HTTP is blocked.

The pure HTTP fallback can also crawl the rendered page preload JSON from
regular Python requests. This needs a reusable browser cookie when Cloudflare
blocks direct requests:

```powershell
$env:BGG_COOKIE = "cf_clearance=...; other_cookie=..."
python .\bgg_crawler.py crawl-html --ranks-csv data\bgg_browse_candidates.csv --db data\bgg_games.sqlite --resume --workers 2 --page-delay 1.5
```

Keep `--workers` small. BGG pages are protected by Cloudflare and this crawler
should be treated as a polite cache builder, not a high-throughput scraper.

OpenCLI is only a slow browser fallback for smoke tests or a small number of
records. Start the daemon and make sure the Browser Bridge extension is
connected:

```powershell
opencli daemon restart
opencli daemon status
```

Then crawl details through rendered BGG pages:

```powershell
python .\bgg_crawler.py crawl-opencli --ranks-csv data\bgg_browse_candidates.csv --db data\bgg_games.sqlite --resume
```

This mode is slower than XML API crawling, but it can extract the frontend
`window.GEEK.geekitemPreload.item` structure without a BGG API token.

Run a small test crawl:

```powershell
python .\bgg_crawler.py crawl --ranks-csv data\bg_ranks.csv --db data\bgg_games.sqlite --limit 50 --resume
```

Useful options:

```powershell
python .\bgg_crawler.py crawl --min-users-rated 100 --recent-min-users-rated 30 --recent-years 3 --exclude-expansions --resume
```

## Output Tables

- `games`: core recommendation fields, ratings, ownership counts, weight, raw JSON.
- `game_links`: categories, mechanics, families, designers, artists, publishers.
- `game_versions`: version names, languages, publishers.
- `game_polls`: raw poll data such as suggested player count and language dependence.

## Skill and Database Snapshot

The first minimal Codex skill lives at:

```text
skills/board-game-recommender
```

This v0.1 skill only explains and queries the local BGG SQLite database. It does
not include recommendation policy yet.

The first publishable database snapshot lives at:

```text
releases/v0.1/bgg_games_v0.1.sqlite
```

The release manifest with SHA-256 checksum and table counts is:

```text
releases/v0.1/manifest.json
```
