# Tennis head-to-head stats in Python (ATP & WTA)

Small, runnable examples for pulling tennis **head-to-head records** and
**player match history** into pandas, using the
[Tennis Player Stats & H2H Scraper](https://apify.com/incognito_mode/tennis-player-stats-h2h-scraper)
on Apify (data from Sofascore).

| Script | What it does |
| --- | --- |
| `h2h.py` | `python h2h.py "Sinner vs Alcaraz"`: overall tally, split by surface, last 5 meetings, every meeting saved to `h2h.csv` |
| `career.py` | `python career.py "Iga Swiatek" --stats`: last two years of matches, win % by surface per year, first-serve % per match |
| `common.py` | Runs the Actor and flattens rows into a DataFrame |

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export APIFY_TOKEN=...   # https://console.apify.com/settings/integrations
```

The free Apify plan's monthly credit covers these examples. A head-to-head is
a few cents, and a player's two years with serve stats is well under $1.

## How the data is shaped

- One row per match from a player's side: `perspectivePlayer`, `opponent`,
  `won`, `scoreForPlayer`, `surfaceCategory`, `tournamentName`, `round`, and
  more.
- Each pair also gets a free `rowType: "h2h"` row with `playerAWins`,
  `playerBWins` and `bySurface`.
- `statistics` and `odds` keep Sofascore's home/away order (`player1` =
  home). `common.stat_for_player` picks the right side for you.

## License

MIT for the code in this repository. Check Sofascore's terms for how you use
the data.
