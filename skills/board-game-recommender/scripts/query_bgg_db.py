#!/usr/bin/env python3
"""Query a local BoardGameGeek SQLite cache."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any


GAME_COLUMNS = [
    "bgg_id",
    "primary_name",
    "year_published",
    "min_players",
    "max_players",
    "min_playtime",
    "max_playtime",
    "playing_time",
    "min_age",
    "average",
    "bayes_average",
    "users_rated",
    "rank",
    "owned",
    "trading",
    "wanting",
    "wishing",
    "average_weight",
    "num_weights",
    "image",
    "thumbnail",
    "source_fetched_at",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_db_candidates() -> list[Path]:
    root = project_root()
    candidates: list[Path] = []
    env_path = os.environ.get("BGG_DB_PATH")
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            root / "releases" / "v0.1" / "bgg_games_v0.1.sqlite",
            root / "data" / "bgg_games.sqlite",
        ]
    )
    return candidates


def resolve_db(path: str | None) -> Path:
    if path:
        db = Path(path)
        if not db.exists():
            raise SystemExit(f"Database not found: {db}")
        return db
    for candidate in default_db_candidates():
        if candidate.exists():
            return candidate
    choices = "\n".join(str(p) for p in default_db_candidates())
    raise SystemExit(f"No database found. Checked:\n{choices}")


def connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def print_json(payload: Any) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def fetch_links(con: sqlite3.Connection, bgg_id: int) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        SELECT link_type, link_id, value
        FROM game_links
        WHERE bgg_id = ?
        ORDER BY link_type, value
        """,
        (bgg_id,),
    ).fetchall()
    return rows_to_dicts(rows)


def fetch_versions(con: sqlite3.Connection, bgg_id: int) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        SELECT version_id, name, year_published, language, publisher
        FROM game_versions
        WHERE bgg_id = ?
        ORDER BY name, version_id
        """,
        (bgg_id,),
    ).fetchall()
    return rows_to_dicts(rows)


def fetch_polls(con: sqlite3.Connection, bgg_id: int, include_raw: bool) -> list[dict[str, Any]]:
    columns = "poll_name, title, total_votes, raw_json" if include_raw else "poll_name, title, total_votes"
    rows = con.execute(
        f"""
        SELECT {columns}
        FROM game_polls
        WHERE bgg_id = ?
        ORDER BY poll_name
        """,
        (bgg_id,),
    ).fetchall()
    return rows_to_dicts(rows)


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", help="Path to the SQLite database. Defaults to BGG_DB_PATH, releases/v0.1, then data/.")


def cmd_schema(args: argparse.Namespace) -> None:
    db = resolve_db(args.db)
    con = connect(db)
    tables: dict[str, Any] = {}
    for row in con.execute(
        """
        SELECT name, sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ):
        name = row["name"]
        columns = rows_to_dicts(con.execute(f'PRAGMA table_info("{name}")').fetchall())
        count = con.execute(f'SELECT count(*) AS n FROM "{name}"').fetchone()["n"]
        tables[name] = {"count": count, "create_sql": row["sql"], "columns": columns}
    indexes = rows_to_dicts(
        con.execute(
            """
            SELECT name, tbl_name, sql
            FROM sqlite_master
            WHERE type = 'index'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
    )
    con.close()
    print_json({"database": str(db), "tables": tables, "indexes": indexes})


def cmd_search(args: argparse.Namespace) -> None:
    db = resolve_db(args.db)
    con = connect(db)
    where = []
    params: list[Any] = []

    if args.name:
        where.append("lower(g.primary_name) LIKE '%' || lower(?) || '%'")
        params.append(args.name)
    if args.players is not None:
        where.append("g.min_players <= ? AND g.max_players >= ?")
        params.extend([args.players, args.players])
    if args.max_playtime is not None:
        where.append("g.playing_time <= ?")
        params.append(args.max_playtime)
    if args.min_playtime is not None:
        where.append("g.playing_time >= ?")
        params.append(args.min_playtime)
    if args.min_rating is not None:
        where.append("g.average >= ?")
        params.append(args.min_rating)
    if args.min_users_rated is not None:
        where.append("g.users_rated >= ?")
        params.append(args.min_users_rated)
    if args.max_weight is not None:
        where.append("g.average_weight <= ?")
        params.append(args.max_weight)
    if args.min_weight is not None:
        where.append("g.average_weight >= ?")
        params.append(args.min_weight)
    if args.year_from is not None:
        where.append("g.year_published >= ?")
        params.append(args.year_from)
    if args.year_to is not None:
        where.append("g.year_published <= ?")
        params.append(args.year_to)
    if args.link_type and args.link_value:
        where.append(
            """
            EXISTS (
              SELECT 1 FROM game_links l
              WHERE l.bgg_id = g.bgg_id
                AND l.link_type = ?
                AND lower(l.value) LIKE '%' || lower(?) || '%'
            )
            """
        )
        params.extend([args.link_type, args.link_value])

    where_sql = "WHERE " + " AND ".join(f"({part})" for part in where) if where else ""
    order_sql = {
        "rank": "g.rank IS NULL, g.rank ASC, g.users_rated DESC",
        "rating": "g.average IS NULL, g.average DESC, g.users_rated DESC",
        "users_rated": "g.users_rated DESC, g.rank IS NULL, g.rank ASC",
        "weight": "g.average_weight IS NULL, g.average_weight ASC, g.rank IS NULL, g.rank ASC",
    }[args.order_by]
    columns = ", ".join(f"g.{col}" for col in GAME_COLUMNS)
    sql = f"""
        SELECT {columns}
        FROM games g
        {where_sql}
        ORDER BY {order_sql}
        LIMIT ?
    """
    params.append(args.limit)
    rows = rows_to_dicts(con.execute(sql, params).fetchall())

    if args.include_links:
        for row in rows:
            row["links"] = fetch_links(con, int(row["bgg_id"]))

    con.close()
    print_json({"database": str(db), "count": len(rows), "results": rows})


def cmd_game(args: argparse.Namespace) -> None:
    db = resolve_db(args.db)
    con = connect(db)
    columns = ", ".join(GAME_COLUMNS + (["description", "raw_json"] if args.include_raw else ["description"]))
    row = con.execute(f"SELECT {columns} FROM games WHERE bgg_id = ?", (args.id,)).fetchone()
    if row is None:
        con.close()
        print_json({"database": str(db), "game": None})
        return
    game = dict(row)
    game["links"] = fetch_links(con, args.id)
    game["versions"] = fetch_versions(con, args.id)
    game["polls"] = fetch_polls(con, args.id, args.include_raw)
    con.close()
    print_json({"database": str(db), "game": game})


def cmd_links(args: argparse.Namespace) -> None:
    db = resolve_db(args.db)
    con = connect(db)
    where = []
    params: list[Any] = []
    if args.type:
        where.append("link_type = ?")
        params.append(args.type)
    if args.value:
        where.append("lower(value) LIKE '%' || lower(?) || '%'")
        params.append(args.value)
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    rows = rows_to_dicts(
        con.execute(
            f"""
            SELECT link_type, link_id, value, count(*) AS game_count
            FROM game_links
            {where_sql}
            GROUP BY link_type, link_id, value
            ORDER BY game_count DESC, link_type, value
            LIMIT ?
            """,
            [*params, args.limit],
        ).fetchall()
    )
    con.close()
    print_json({"database": str(db), "count": len(rows), "results": rows})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    schema = subparsers.add_parser("schema", help="Print database schema and table counts.")
    add_common_args(schema)
    schema.set_defaults(func=cmd_schema)

    search = subparsers.add_parser("search", help="Search and filter games.")
    add_common_args(search)
    search.add_argument("--name", help="Partial game name.")
    search.add_argument("--players", type=int, help="Required supported player count.")
    search.add_argument("--min-playtime", type=int, help="Minimum playing_time in minutes.")
    search.add_argument("--max-playtime", type=int, help="Maximum playing_time in minutes.")
    search.add_argument("--min-rating", type=float, help="Minimum average rating.")
    search.add_argument("--min-users-rated", type=int, default=0, help="Minimum users_rated. Default: 0.")
    search.add_argument("--min-weight", type=float, help="Minimum average_weight.")
    search.add_argument("--max-weight", type=float, help="Maximum average_weight.")
    search.add_argument("--year-from", type=int, help="Minimum year_published.")
    search.add_argument("--year-to", type=int, help="Maximum year_published.")
    search.add_argument("--link-type", help="Filter by game_links.link_type. Use with --link-value.")
    search.add_argument("--link-value", help="Partial game_links.value. Use with --link-type.")
    search.add_argument("--include-links", action="store_true", help="Include links for each returned game.")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--order-by", choices=["rank", "rating", "users_rated", "weight"], default="rank")
    search.set_defaults(func=cmd_search)

    game = subparsers.add_parser("game", help="Fetch one game by BGG id.")
    add_common_args(game)
    game.add_argument("--id", type=int, required=True, help="BGG game id.")
    game.add_argument("--include-raw", action="store_true", help="Include raw_json fields.")
    game.set_defaults(func=cmd_game)

    links = subparsers.add_parser("links", help="List link values and counts.")
    add_common_args(links)
    links.add_argument("--type", help="Filter by link_type.")
    links.add_argument("--value", help="Partial value filter.")
    links.add_argument("--limit", type=int, default=50)
    links.set_defaults(func=cmd_links)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
