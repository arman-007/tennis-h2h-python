"""A player's form this season and last: win rate by surface, and first-serve %.

Usage:  python career.py "Iga Swiatek" [--stats]
Saves win_rate_by_surface.png (and first_serve.png with --stats).
"""

from __future__ import annotations

import sys
from datetime import date

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from common import matches_frame, run_actor, stat_for_player

# One color per surface, always the same one, whichever surfaces a player has.
SURFACE_COLORS = {"hard": "#2a78d6", "clay": "#eb6834", "grass": "#1baf7a"}
INK, MUTED, SURFACE = "#2b2b29", "#5c5b56", "#fcfcfb"
plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": "#c3c2b7",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": "#e5e4df",
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
    }
)


def win_rate_by_surface(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Win % and match count per season and surface."""
    rate = df.pivot_table(index="season", columns="surface", values="won", aggfunc="mean") * 100
    count = pd.crosstab(df["season"], df["surface"])
    surfaces = [s for s in SURFACE_COLORS if s in rate.columns]
    return rate[surfaces], count[surfaces]


def plot_win_rate(name: str, rate: pd.DataFrame, count: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.8 / len(rate.columns)
    for i, surface in enumerate(rate.columns):
        offset = (i - (len(rate.columns) - 1) / 2) * width
        xs = [n + offset for n in range(len(rate))]
        bars = ax.bar(xs, rate[surface].fillna(0), width, color=SURFACE_COLORS[surface],
                      edgecolor=SURFACE, linewidth=2, label=surface)
        labels = [f"{v:.0f}%\n{c} played" if c else "" for v, c in zip(rate[surface], count[surface])]
        ax.bar_label(bars, labels=labels, fontsize=8, color=MUTED, padding=3)
    ax.set_xticks(range(len(rate)), [str(s) for s in rate.index])
    ax.set_ylim(0, 125)
    ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel("matches won (%)")
    ax.set_title(f"{name}: matches won by surface", loc="left")
    ax.legend(frameon=False, ncols=len(rate.columns), loc="upper right")
    fig.tight_layout()
    fig.savefig("win_rate_by_surface.png", dpi=150)


def plot_first_serve(name: str, rows: list[dict]) -> int:
    matches = [r for r in rows if r.get("rowType") == "match"]
    points = pd.DataFrame(
        {"date": pd.to_datetime([r["startTimeIso"] for r in matches]),
         "first_serve": [stat_for_player(r, "firstServeAccuracy") for r in matches]}
    ).dropna().sort_values("date")
    average = points["first_serve"].rolling(10).mean()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(points["date"], points["first_serve"], s=14, color="#2a78d6", alpha=0.35, linewidths=0)
    ax.plot(points["date"], average, color="#2a78d6", linewidth=2)
    ax.annotate("10-match average", (points["date"].iloc[-1], average.iloc[-1]), xytext=(0, 12),
                textcoords="offset points", ha="right", fontsize=8, color=MUTED)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.set_ylabel("first serves in (%)")
    ax.set_title(f"{name}: first-serve % per match", loc="left")
    fig.tight_layout()
    fig.savefig("first_serve.png", dpi=150)
    return len(points)


def main(player: str, with_stats: bool) -> None:
    since = f"{date.today().year - 1}-01-01"  # this season and last, so a re-run stays current
    run_input = {"players": [player], "maxMatchesPerPlayer": 0, "dateFrom": since}
    if with_stats:
        run_input["matchDetails"] = ["statistics"]
    rows = run_actor(run_input)
    df = matches_frame(rows)
    if df.empty:
        sys.exit("No matches came back; check the run log for the player name.")

    name = df["player"].iloc[0]
    df["season"] = df["date"].dt.year
    rate, count = win_rate_by_surface(df)
    print(f"\n{name}: {len(df)} matches since {since}, {df['won'].mean():.0%} won\n")
    print(rate.round(1).astype(str).add("% of ").add(count.astype(str)).to_string(), "\n")

    plot_win_rate(name, rate, count)
    print("Saved win_rate_by_surface.png")
    if with_stats:
        n = plot_first_serve(name, rows)
        print(f"Saved first_serve.png ({n} matches with statistics)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0] if args else "Iga Swiatek", "--stats" in sys.argv)
