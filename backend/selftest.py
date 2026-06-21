"""Run every registered spot through the engine — no database required.

    uv run python selftest.py                         # all spots, date = tomorrow
    uv run python selftest.py <spot_key>              # one spot
    uv run python selftest.py <spot_key> 2026-06-21   # one spot, explicit date
"""
import datetime as dt
import sys

from app.engine import run_check
from app.spots import load_spots
from app.spots.render import render


def main() -> None:
    wanted = sys.argv[1] if len(sys.argv) > 1 else None
    on_date = (
        dt.date.fromisoformat(sys.argv[2])
        if len(sys.argv) > 2
        else dt.date.today() + dt.timedelta(days=1)
    )
    print(f"Using date: {on_date}\n")

    for key, spot in load_spots().items():
        if wanted and key != wanted:
            continue
        print("=" * 70)
        print(f"{spot.key}  —  {spot.name}")
        print(f"  headless={spot.headless}")
        steps = render(spot.steps, on_date)
        condition = render(spot.condition, on_date)
        r = run_check(spot.url, steps, condition, headless=spot.headless)
        if r["error"]:
            print(f"  ERROR   : {r['error']}")
        else:
            print(f"  observed: {r['observed']}")
            print(f"  MET (would notify): {r['met']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
