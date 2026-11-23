"""Head-to-head between two tennis players.

Usage:  python h2h.py "Sinner vs Alcaraz"
Prints the tally, the split by surface and the last five meetings, and saves
h2h.csv with every meeting.
"""

from __future__ import annotations

import sys

import pandas as pd

from common import matches_frame, run_actor


def main(matchup: str) -> None:
    rows = run_actor({"matchups": [matchup]})
    summary = next((r for r in rows if r.get("rowType") == "h2h"), None)
    if summary is None:
        sys.exit("No head-to-head came back; check the run log for the player names.")

    a, b = summary["playerA"]["name"], summary["playerB"]["name"]
    print(f"\n{a} {summary['playerAWins']}-{summary['playerBWins']} {b} "
          f"({summary['totalMeetings']} meetings)\n")

    by_surface = pd.DataFrame(summary["bySurface"]).T.rename(columns={"playerAWins": a, "playerBWins": b})
    print(by_surface.to_string(), "\n")

    frame = matches_frame(rows)
    meetings = frame[frame["source"] == "matchup"]
    print(meetings.tail(5)[["date", "tournament", "round", "surface", "won", "score"]].to_string(index=False))
    meetings.to_csv("h2h.csv", index=False)
    print("\nSaved every meeting to h2h.csv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Sinner vs Alcaraz")
