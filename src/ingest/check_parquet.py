
from pathlib import Path

import duckdb

year = 2022
parquet_path = Path(f"data/processed/stationary-{year}.parquet")

if not parquet_path.exists():
    raise FileNotFoundError(f"Missing file: {parquet_path}")

con = duckdb.connect()

result = con.execute(
    """
    SELECT
        COUNT(*) AS row_count,
        MIN(datetime_bin) AS first_observation,
        MAX(datetime_bin) AS last_observation,
        COUNT(DISTINCT sign_id) AS unique_signs,
        SUM(volume) AS total_vehicles
    FROM read_parquet(?)
    """,
    [str(parquet_path)]
).fetchone()

print(f"Year: {year}")
print(f"Rows: {result[0]:,}")
print(f"First observation: {result[1]}")
print(f"Last observation: {result[2]}")
print(f"Unique signs: {result[3]:,}")
print(f"Total vehicles: {result[4]:,}")