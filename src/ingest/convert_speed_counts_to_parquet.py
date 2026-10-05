from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


INPUT_FILE = Path("data/raw/stationary-2026.csv")
OUTPUT_FILE = Path("data/processed/stationary-2026.parquet")

CHUNK_SIZE = 250_000

writer = None

for chunk in pd.read_csv(
    INPUT_FILE,
    chunksize=CHUNK_SIZE,
):
    chunk["datetime_bin"] = pd.to_datetime(chunk["datetime_bin"])

    table = pa.Table.from_pandas(
        chunk,
        preserve_index=False,
    )

    if writer is None:
        writer = pq.ParquetWriter(
            OUTPUT_FILE,
            table.schema,
        )

    writer.write_table(table)

    print(f"Processed {len(chunk):,} rows")

if writer is not None:
    writer.close()

print(f"Created: {OUTPUT_FILE}")