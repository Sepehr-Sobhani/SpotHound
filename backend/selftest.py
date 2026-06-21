"""Run the reference targets through the engine — no database required.

    uv run python selftest.py
"""
from app.engine import run_check
from app.targets_data import REFERENCE_TARGETS


def main() -> None:
    for t in REFERENCE_TARGETS:
        print("=" * 70)
        print(t["name"])
        print(f"  headless={t.get('headless', True)}")
        r = run_check(t["url"], t["steps"], t["condition"], headless=t.get("headless", True))
        if r["error"]:
            print(f"  ERROR   : {r['error']}")
        else:
            print(f"  observed: {r['observed']}")
            print(f"  MET (would notify): {r['met']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
