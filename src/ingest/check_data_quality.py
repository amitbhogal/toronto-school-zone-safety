from pathlib import Path
import re

import pandas as pd


PROCESSED_DIR = Path("data/processed")

EXPECTED_COLUMNS = [
    "sign_id",
    "address",
    "dir",
    "datetime_bin",
    "speed_bin",
    "volume",
]


def check_year(year: int) -> None:
    path = PROCESSED_DIR / f"stationary-{year}.parquet"

    print("\n" + "=" * 70)
    print(f"YEAR: {year}")
    print("=" * 70)

    if not path.exists():
        print("❌ FILE NOT FOUND")
        return

    df = pd.read_parquet(path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    # 1. Schema
    if list(df.columns) == EXPECTED_COLUMNS:
        print("✅ Schema: correct")
    else:
        print("❌ Schema: unexpected columns")

    # 2. Missing values
    print("\nMissing values:")
    missing = df[EXPECTED_COLUMNS].isna().sum()

    if missing.sum() == 0:
        print("✅ No missing values")
    else:
        for column, count in missing.items():
            if count:
                print(f"⚠️  {column}: {count:,}")

    # 3. Data types
    print("\nData types:")
    for column in EXPECTED_COLUMNS:
        print(f"  {column}: {df[column].dtype}")

    # 4. Sign IDs
    bad_sign_ids = pd.to_numeric(df["sign_id"], errors="coerce").isna().sum()

    if bad_sign_ids == 0:
        print("✅ Sign IDs are numeric")
    else:
        print(f"❌ Invalid sign IDs: {bad_sign_ids:,}")

    # 5. Volume
    bad_volume = (df["volume"] < 0).sum()

    if bad_volume == 0:
        print("✅ No negative vehicle volumes")
    else:
        print(f"❌ Negative volumes: {bad_volume:,}")

    # 6. Dates
    dates = pd.to_datetime(df["datetime_bin"], errors="coerce")

    invalid_dates = dates.isna().sum()

    if invalid_dates == 0:
        print("✅ All timestamps are valid")
    else:
        print(f"❌ Invalid timestamps: {invalid_dates:,}")

    wrong_year = (dates.dt.year != year).sum()

    if wrong_year == 0:
        print(f"✅ All timestamps belong to {year}")
    else:
        print(f"⚠️  Timestamps belonging to another year: {wrong_year:,}")

    print(f"Date range: {dates.min()} → {dates.max()}")

    # 7. Speed-bin format
    speed_bins = df["speed_bin"].dropna().astype(str).unique()

    bad_bins = []

    pattern = re.compile(r"^\[\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)$")

    for value in speed_bins:
        match = pattern.match(value)

        if not match:
            bad_bins.append(value)
            continue

        lower = float(match.group(1))
        upper = float(match.group(2))

        if upper <= lower:
            bad_bins.append(value)

    if not bad_bins:
        print("✅ Speed-bin format looks consistent")
    else:
        print(f"⚠️  Unusual speed bins: {bad_bins[:10]}")

    # 8. Basic range checks
    print("\nBasic ranges:")
    print(f"  Unique signs: {df['sign_id'].nunique():,}")
    print(f"  Total vehicles: {df['volume'].sum():,}")
    print(f"  Unique speed bins: {df['speed_bin'].nunique():,}")

    print("\nResult: quality scan complete")


def main() -> None:
    years = range(2017, 2027)

    print("Toronto School Zone Safety Analysis")
    print("Historical Speed Data Quality Check")
    print("Scanning 2017–2026")

    for year in years:
        check_year(year)

    print("\n" + "=" * 70)
    print("ALL YEARS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()