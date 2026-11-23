"""A player's last two years: win rate by surface, and first-serve %.

Usage:  python career.py "Iga Swiatek" [--stats]
Saves win_rate_by_surface.png (and first_serve.png with --stats).
"""

from __future__ import annotations

import sys

import matplotlib.pyplot as plt

from common import matches_frame, run_actor, stat_for_player


def main(player: str, with_stats: bool) -> None:
    run_input = {"players": [player], "maxMatchesPerPlayer": 0, "dateFrom": "2 years"}
    if with_stats:
        run_input["matchDetails"] = ["statistics"]
    rows = run_actor(run_input)
    df = matches_frame(rows)
    if df.empty:
        sys.exit("No matches came back; check the run log for the player name.")

    df["year"] = df["date"].dt.year
    rate = df.pivot_table(index="year", columns="surface", values="won", aggfunc="mean") * 100
    print(f"\n{df['player'].iloc[0]}: {len(df)} matches, {df['won'].mean():.0%} won\n")
    print(rate.round(1).to_string(), "\n")

    ax = rate.plot(kind="bar", ylim=(0, 100), title=f"{df['player'].iloc[0]}: win % by surface")
    ax.set_ylabel("matches won (%)")
    plt.tight_layout()
    plt.savefig("win_rate_by_surface.png", dpi=150)
    print("Saved win_rate_by_surface.png")

    if with_stats:
        match_rows = sorted((r for r in rows if r.get("rowType") == "match"), key=lambda r: r["startTimeIso"])
        points = [(r["startTimeIso"][:10], stat_for_player(r, "firstServeAccuracy")) for r in match_rows]
        points = [(d, v) for d, v in points if v is not None]
        plt.figure()
        plt.plot([d for d, _ in points], [v for _, v in points], marker=".")
        plt.xticks(rotation=60, fontsize=6)
        plt.ylabel("first serves in (%)")
        plt.title(f"{df['player'].iloc[0]}: first-serve % per match")
        plt.tight_layout()
        plt.savefig("first_serve.png", dpi=150)
        print(f"Saved first_serve.png ({len(points)} matches with statistics)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0] if args else "Iga Swiatek", "--stats" in sys.argv)
