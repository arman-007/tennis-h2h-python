"""Shared helpers: run the Apify Actor and load its rows into pandas."""

from __future__ import annotations

import os
import sys

import pandas as pd
from apify_client import ApifyClient

ACTOR = "incognito_mode/tennis-player-stats-h2h-scraper"


def run_actor(run_input: dict) -> list[dict]:
    """Run the Actor and return its dataset rows. Reads APIFY_TOKEN from the environment."""
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first: https://console.apify.com/settings/integrations")
    client = ApifyClient(token)
    run = client.actor(ACTOR).call(run_input=run_input)
    if run is None:
        sys.exit("The run did not start.")
    rows = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    cost = run.get("usageTotalUsd") or 0
    print(f"Run {run['status']}: {len(rows)} rows, about ${cost:.3f}")
    return rows


def matches_frame(rows: list[dict]) -> pd.DataFrame:
    """One row per match, flattened to the columns most analyses need."""
    matches = [r for r in rows if r.get("rowType") == "match"]
    df = pd.DataFrame(
        {
            "date": pd.to_datetime([r["startTimeIso"] for r in matches]),
            "player": [r["perspectivePlayer"]["name"] for r in matches],
            "opponent": [r["opponent"]["name"] for r in matches],
            "opponent_rank": [r["opponent"].get("ranking") for r in matches],
            "won": [r["won"] for r in matches],
            "score": [r["scoreForPlayer"] for r in matches],
            "surface": [r["surfaceCategory"] for r in matches],
            "tournament": [r["tournamentName"] for r in matches],
            "round": [(r.get("round") or {}).get("name") for r in matches],
            "result_type": [r["resultType"] for r in matches],
            "source": [r["source"] for r in matches],  # "matchup" or "player"
        }
    )
    return df.sort_values("date").reset_index(drop=True)


def stat_for_player(row: dict, key: str) -> float | None:
    """A percentage stat (e.g. firstServeAccuracy) for the row's perspective player.

    Statistics keep Sofascore's home/away order (player1 = home), so pick the
    side that matches perspectivePlayer.
    """
    side = "player1" if row["player1"]["id"] == row["perspectivePlayer"]["id"] else "player2"
    for stat in row.get("statistics") or []:
        if stat["period"] == "ALL" and stat["key"] == key and stat.get(f"{side}Total"):
            return 100 * stat[side] / stat[f"{side}Total"]
    return None
