from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/raw/watch_your_speed_locations.csv")
OUTPUT_FILE = Path("data/processed/watch_your_speed_locations.parquet")


df = pd.read_csv(INPUT_FILE)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df.to_parquet(OUTPUT_FILE, index=False)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Created: {OUTPUT_FILE}")