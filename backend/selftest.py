"""Run every registered spot through the engine — no database required.

    uv run python selftest.py            # all spots
    uv run python selftest.py <spot_key> # just one
"""
import sys

from app.engine import run_check
from app.spots import load_spots


def main() -> None:
    wanted = sys.argv[1] if len(sys.argv) > 1 else None
    spots = load_spots()
    for key, spot in spots.items():
        if wanted and key != wanted:
            continue
        print("=" * 70)
        print(f"{spot.key}  —  {spot.name}")
        print(f"  headless={spot.headless}")
        r = run_check(spot.url, spot.steps, spot.condition, headless=spot.headless)
        if r["error"]:
            print(f"  ERROR   : {r['error']}")
        else:
            print(f"  observed: {r['observed']}")
            print(f"  MET (would notify): {r['met']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
