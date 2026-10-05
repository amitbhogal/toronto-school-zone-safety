from pathlib import Path
import json
import re

import pandas as pd


# ============================================================
# PROJECT SETTINGS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROCESSED_DIR / "dashboard"

YEARS = list(range(2017, 2027))


# +10 km/h is the default in the dashboard.
DEFAULT_THRESHOLD = 10

MAX_THRESHOLD = 70
THRESHOLDS = list(range(5, MAX_THRESHOLD + 1, 5))


# ============================================================
# FILE HELPERS
# ============================================================

def find_speed_file(year):
    """
    Find the processed speed-count Parquet file for a year.

    Current project naming convention:
        stationary-2017.parquet
        stationary-2018.parquet
        ...
        stationary-2026.parquet
    """

    path = PROCESSED_DIR / f"stationary-{year}.parquet"

    if path.exists():
        return path

    return None


def find_location_file():
    """
    Find the Watch Your Speed location metadata file.
    """

    parquet_path = (
        PROCESSED_DIR / "watch_your_speed_locations.parquet"
    )

    csv_path = (
        PROCESSED_DIR / "watch_your_speed_locations.csv"
    )

    if parquet_path.exists():
        return parquet_path

    if csv_path.exists():
        return csv_path

    raise FileNotFoundError(
        "Could not find watch_your_speed_locations.parquet "
        "or watch_your_speed_locations.csv."
    )


# ============================================================
# SPEED-BIN PARSING
# ============================================================

def parse_speed_lower_bound(speed_bin):
    """
    Extract the lower bound from a speed bin.

    Examples:

        [30,35)  -> 30
        [50,55)  -> 50
        [95,100) -> 95
        [100,)   -> 100

    The lower bound is what we use when determining whether
    a vehicle belongs to an elevated-speed threshold.
    """

    if pd.isna(speed_bin):
        return None

    match = re.match(
        r"^\[\s*(\d+(?:\.\d+)?)",
        str(speed_bin),
    )

    if not match:
        return None

    return float(match.group(1))


# ============================================================
# LOCATION METADATA
# ============================================================

def load_locations():
    """
    Load Watch Your Speed location metadata.

    The location table supplies:

        sign_id
        ward_no
        speed_limit
        address
        dir

    The dashboard population is limited to current 30 km/h
    locations with a known ward.
    """

    location_file = find_location_file()

    print()
    print(f"Loading location metadata: {location_file.name}")

    if location_file.suffix.lower() == ".parquet":
        locations = pd.read_parquet(location_file)
    else:
        locations = pd.read_csv(location_file)

    required_columns = {
        "sign_id",
        "ward_no",
        "speed_limit",
        "address",
        "dir",
    }

    missing_columns = (
        required_columns - set(locations.columns)
    )

    if missing_columns:
        raise ValueError(
            "Location file is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    # Keep only fields needed by the transformation layer.
    columns = [
        "sign_id",
        "ward_no",
        "speed_limit",
        "address",
        "dir",
    ]

    # These may exist in the location file, but are not used
    # as a gatekeeper for whether a speed observation counts.
    if "start_date" in locations.columns:
        columns.append("start_date")

    if "end_date" in locations.columns:
        columns.append("end_date")

    locations = locations[columns].copy()

    # Normalize sign IDs.
    locations["sign_id"] = pd.to_numeric(
        locations["sign_id"],
        errors="coerce",
    ).astype("Int64")

    # Normalize ward numbers.
    locations["ward_no"] = pd.to_numeric(
        locations["ward_no"],
        errors="coerce",
    ).astype("Int64")

    # Normalize speed limits.
    locations["speed_limit"] = pd.to_numeric(
        locations["speed_limit"],
        errors="coerce",
    )

    # Main dashboard population:
    # current locations operating at 30 km/h.
    locations = locations[
        locations["speed_limit"] == 30
    ].copy()

    # One metadata record per sign.
    locations = locations.drop_duplicates(
        subset=["sign_id"],
        keep="first",
    )

    print(
        f"Current 30 km/h locations: "
        f"{locations['sign_id'].nunique():,}"
    )

    print(
        f"Current 30 km/h locations with a ward: "
        f"{locations['ward_no'].notna().sum():,}"
    )

    print(
        f"Current 30 km/h locations without a ward: "
        f"{locations['ward_no'].isna().sum():,}"
    )

    return locations


# ============================================================
# ONE YEAR OF DATA
# ============================================================

def process_year(year, speed_file, locations):
    """
    Process one year of speed observations.

    Produces three levels:

        location/year
        location/month
        location/day

    Processing one year at a time prevents us from loading
    all historical observations into memory simultaneously.
    """

    print()
    print("=" * 60)
    print(f"PROCESSING {year}")
    print("=" * 60)

    print(f"Reading: {speed_file.name}")

    df = pd.read_parquet(speed_file)

    required_columns = {
        "sign_id",
        "datetime_bin",
        "speed_bin",
        "volume",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"{year} is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    # --------------------------------------------------------
    # Normalize fields
    # --------------------------------------------------------

    df["sign_id"] = pd.to_numeric(
        df["sign_id"],
        errors="coerce",
    ).astype("Int64")

    df["datetime_bin"] = pd.to_datetime(
        df["datetime_bin"],
        errors="coerce",
    )

    df["volume"] = pd.to_numeric(
        df["volume"],
        errors="coerce",
    )

    # Remove unusable observations.
    df = df[
        df["sign_id"].notna()
        & df["datetime_bin"].notna()
        & df["volume"].notna()
        & (df["volume"] >= 0)
    ].copy()

    # --------------------------------------------------------
    # Convert speed bins to lower-bound speeds
    # --------------------------------------------------------

    df["speed_lower"] = df["speed_bin"].apply(
        parse_speed_lower_bound
    )

    df = df[
        df["speed_lower"].notna()
    ].copy()

    # --------------------------------------------------------
    # JOIN SPEED OBSERVATIONS TO LOCATION METADATA
    # --------------------------------------------------------

    df = df.merge(
        locations,
        on="sign_id",
        how="inner",
        suffixes=("", "_location"),
    )

    print(
        f"Observations after joining to current 30 km/h "
        f"locations: {len(df):,}"
    )

    # --------------------------------------------------------
    # Ward is required for the public Ward → Location
    # hierarchy.
    #
    # We do NOT invent a ward for unresolved historical IDs.
    # --------------------------------------------------------

    unresolved = df["ward_no"].isna().sum()

    if unresolved:
        print(
            f"Excluding {unresolved:,} observations from "
            f"locations without ward metadata."
        )

    df = df[
        df["ward_no"].notna()
    ].copy()

    # --------------------------------------------------------
    # Time fields
    # --------------------------------------------------------

    df["year"] = df["datetime_bin"].dt.year
    df["month"] = df["datetime_bin"].dt.month

    df["date"] = (
        df["datetime_bin"]
        .dt.strftime("%Y-%m-%d")
    )

    # --------------------------------------------------------
    # Threshold flags
    #
    # Example:
    #
    # posted speed = 30
    # threshold = +10
    # cutoff = 40
    #
    # A [40,45) observation qualifies.
    # A [35,40) observation does not.
    # --------------------------------------------------------

    for threshold in THRESHOLDS:

        cutoff = (
            df["speed_limit"] + threshold
        )

        df[f"eligible_{threshold}"] = (
            df["speed_lower"] >= cutoff
        )

    # ========================================================
    # LOCATION / YEAR
    # ========================================================

    annual = (
        df.groupby(
            [
                "year",
                "ward_no",
                "sign_id",
                "address",
                "dir",
                "speed_limit",
            ],
            dropna=False,
        )
        .agg(
            vehicles=("volume", "sum"),
        )
        .reset_index()
    )

    annual = add_threshold_metrics(
        annual,
        df,
        group_columns=[
            "year",
            "ward_no",
            "sign_id",
        ],
    )

    # ========================================================
    # LOCATION / MONTH
    # ========================================================

    monthly = (
        df.groupby(
            [
                "year",
                "month",
                "ward_no",
                "sign_id",
                "address",
                "dir",
                "speed_limit",
            ],
            dropna=False,
        )
        .agg(
            vehicles=("volume", "sum"),
        )
        .reset_index()
    )

    monthly = add_threshold_metrics(
        monthly,
        df,
        group_columns=[
            "year",
            "month",
            "ward_no",
            "sign_id",
        ],
    )

    # ========================================================
    # LOCATION / DAY
    # ========================================================

    daily = (
        df.groupby(
            [
                "year",
                "date",
                "ward_no",
                "sign_id",
                "address",
                "dir",
                "speed_limit",
            ],
            dropna=False,
        )
        .agg(
            vehicles=("volume", "sum"),
        )
        .reset_index()
    )

    daily = add_threshold_metrics(
        daily,
        df,
        group_columns=[
            "year",
            "date",
            "ward_no",
            "sign_id",
        ],
    )

    return annual, monthly, daily


# ============================================================
# THRESHOLD METRICS
# ============================================================

def add_threshold_metrics(
    result,
    source,
    group_columns,
):
    """
    Add vehicle counts and percentages for each threshold.
    """

    for threshold in THRESHOLDS:

        eligible = (
            source[
                source[f"eligible_{threshold}"]
            ]
            .groupby(
                group_columns,
            )["volume"]
            .sum()
            .rename(
                f"vehicles_{threshold}"
            )
        )

        result = result.merge(
            eligible,
            on=group_columns,
            how="left",
        )

        result[
            f"vehicles_{threshold}"
        ] = (
            result[
                f"vehicles_{threshold}"
            ]
            .fillna(0)
        )

        result[
            f"pct_{threshold}"
        ] = (
            result[
                f"vehicles_{threshold}"
            ]
            / result["vehicles"]
            * 100
        )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("TORONTO SCHOOL ZONE SAFETY")
    print("Dashboard Data Builder")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load location metadata
    # --------------------------------------------------------

    locations = load_locations()

    annual_results = []
    monthly_results = []
    daily_results = []

    # --------------------------------------------------------
    # Process each available year
    # --------------------------------------------------------

    for year in YEARS:

        speed_file = find_speed_file(year)

        if speed_file is None:

            print()
            print(
                f"WARNING: No processed file found for {year}."
            )

            continue

        annual, monthly, daily = process_year(
            year,
            speed_file,
            locations,
        )

        annual_results.append(annual)
        monthly_results.append(monthly)
        daily_results.append(daily)

    # --------------------------------------------------------
    # Make sure something was processed
    # --------------------------------------------------------

    if not annual_results:

        raise RuntimeError(
            "No yearly speed-count files were found."
        )

    # --------------------------------------------------------
    # Combine yearly outputs
    # --------------------------------------------------------

    annual = pd.concat(
        annual_results,
        ignore_index=True,
    )

    monthly = pd.concat(
        monthly_results,
        ignore_index=True,
    )

    daily = pd.concat(
        daily_results,
        ignore_index=True,
    )

    # --------------------------------------------------------
    # Save transformed datasets
    # --------------------------------------------------------

    annual_path = (
        OUTPUT_DIR / "location_annual.parquet"
    )

    monthly_path = (
        OUTPUT_DIR / "location_monthly.parquet"
    )

    daily_path = (
        OUTPUT_DIR / "location_daily.parquet"
    )

    annual.to_parquet(
        annual_path,
        index=False,
    )

    monthly.to_parquet(
        monthly_path,
        index=False,
    )

    daily.to_parquet(
        daily_path,
        index=False,
    )

    # ========================================================
    # LOCATION LOOKUP
    # ========================================================

    location_lookup = (
        annual[
            [
                "ward_no",
                "sign_id",
                "address",
                "dir",
                "speed_limit",
            ]
        ]
        .drop_duplicates(
            subset=["sign_id"],
        )
        .sort_values(
            [
                "ward_no",
                "sign_id",
            ],
        )
    )

    location_lookup_path = (
        OUTPUT_DIR / "locations.json"
    )

    location_lookup.to_json(
        location_lookup_path,
        orient="records",
        indent=2,
    )

    # ========================================================
    # METADATA
    # ========================================================

    dashboard_location_count = int(
        locations[
            locations["ward_no"].notna()
        ]["sign_id"].nunique()
    )

    metadata = {
        "years": YEARS,
        "thresholds": THRESHOLDS,
        "default_threshold": DEFAULT_THRESHOLD,

        "population": {
            "speed_limit": 30,
            "description": (
                "Current Watch Your Speed locations "
                "with a posted speed limit of 30 km/h "
                "and known ward metadata."
            ),
        },

        "calculation": {
            "join_key": "sign_id",
            "speed_lower_bound": True,
            "date_gatekeeper": False,
            "metric": (
                "Percentage of observed vehicles whose "
                "speed-bin lower bound is at least the "
                "posted speed limit plus the selected "
                "threshold."
            ),
        },

        "interpretation": {
            "zero_percent": (
                "Monitoring occurred and none of the "
                "observed vehicles met the selected "
                "threshold."
            ),
            "no_monitoring": (
                "No speed-monitoring observations were "
                "available for that period."
            ),
            "partial_year": (
                "2026 is a partial year and should be "
                "identified as such in the dashboard."
            ),
        },

        "location_count": dashboard_location_count,
    }

    metadata_path = (
        OUTPUT_DIR / "metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)

    print(
        f"Annual rows:  {len(annual):,}"
    )

    print(
        f"Monthly rows: {len(monthly):,}"
    )

    print(
        f"Daily rows:   {len(daily):,}"
    )

    print()
    print("Dashboard output:")

    print(
        f"  {annual_path}"
    )

    print(
        f"  {monthly_path}"
    )

    print(
        f"  {daily_path}"
    )

    print(
        f"  {location_lookup_path}"
    )

    print(
        f"  {metadata_path}"
    )


if __name__ == "__main__":
    main()