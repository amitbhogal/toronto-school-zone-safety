from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

LOCATION_FILE = RAW_DIR / "watch_your_speed_locations.csv"

YEARS = range(2017, 2027)


def main():
    locations = pd.read_csv(LOCATION_FILE)

    print("=" * 70)
    print("SIGN ID → LOCATION JOIN CHECK")
    print("=" * 70)

    print(f"Location rows: {len(locations):,}")
    print(f"Unique location sign IDs: {locations['sign_id'].nunique():,}")

    # Make a clean lookup table.
    lookup = locations[
        ["sign_id", "address", "ward_no", "speed_limit", "start_date", "end_date"]
    ].drop_duplicates("sign_id")

    print("\nLocation table:")
    print(f"  Unique sign IDs: {lookup['sign_id'].nunique():,}")
    print(f"  Missing wards: {lookup['ward_no'].isna().sum():,}")
    print(f"  Missing speed limits: {lookup['speed_limit'].isna().sum():,}")

    all_observed_signs = set()

    for year in YEARS:
        path = PROCESSED_DIR / f"stationary-{year}.parquet"

        df = pd.read_parquet(
            path,
            columns=["sign_id"]
        )

        observed = set(df["sign_id"].unique())
        all_observed_signs.update(observed)

        missing = observed - set(lookup["sign_id"])

        print(
            f"\n{year}: "
            f"{len(observed):,} observed signs | "
            f"{len(missing):,} not found in location table"
        )

        if missing:
            print("  Missing sign IDs:", sorted(missing)[:20])

    print("\n" + "=" * 70)
    print("ALL YEARS")
    print("=" * 70)

    missing_all = all_observed_signs - set(lookup["sign_id"])

    print(f"Unique historical sign IDs: {len(all_observed_signs):,}")
    print(f"Found in location table: {len(all_observed_signs) - len(missing_all):,}")
    print(f"NOT found: {len(missing_all):,}")

    if missing_all:
        print("\nMissing historical sign IDs:")
        print(sorted(missing_all))

    print("\nCheck complete.")


if __name__ == "__main__":
    main()