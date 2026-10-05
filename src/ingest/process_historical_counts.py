
from pathlib import Path
from zipfile import ZipFile
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

# Start with 2017. We'll expand this after validation.
#YEARS_TO_PROCESS = [2018, 2019, 2020, 2021, 2022]
#YEARS_TO_PROCESS = [2022]
YEARS_TO_PROCESS = [2023, 2024, 2025]

CHUNK_SIZE = 250_000

EXPECTED_COLUMNS = [
    "sign_id",
    "address",
    "dir",
    "datetime_bin",
    "speed_bin",
    "volume",
]


def process_csv_stream(csv_file, writer_holder):
    """Read a CSV in chunks and append each chunk to a Parquet writer."""
    for chunk in pd.read_csv(csv_file, chunksize=CHUNK_SIZE):
        # Keep the six expected fields in a consistent order.
        chunk = chunk[EXPECTED_COLUMNS].copy()

        chunk["sign_id"] = pd.to_numeric(chunk["sign_id"], errors="raise").astype("int64")
        chunk["datetime_bin"] = pd.to_datetime(
            chunk["datetime_bin"], errors="raise"
        )
        chunk["volume"] = pd.to_numeric(chunk["volume"], errors="raise").astype("int64")

        # Force text columns to use consistent types, even when
        # a monthly file contains only empty values in a column.
        for column in ["address", "dir", "speed_bin"]:
            chunk[column] = chunk[column].astype("string")

        # Use consistent timestamp precision across all monthly files.
        chunk["datetime_bin"] = chunk["datetime_bin"].astype(
            "datetime64[us]"
        )

        table = pa.Table.from_pandas(chunk, preserve_index=False)

        if writer_holder["writer"] is None:
            output_path = writer_holder["output_path"]
            writer_holder["writer"] = pq.ParquetWriter(output_path, table.schema)

        writer_holder["writer"].write_table(table)
        writer_holder["rows"] += len(chunk)

        print(f"  Processed {writer_holder['rows']:,} rows")



def process_year(year):
    output_path = PROCESSED_DIR / f"stationary-{year}.parquet"
    zip_path = RAW_DIR / f"stationary_detailed_{year}.zip"
    csv_path = RAW_DIR / f"stationary-{year}.csv"
    extracted_dir = RAW_DIR / "2022_test"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    writer_holder = {
        "writer": None,
        "output_path": output_path,
        "rows": 0,
    }

    try:
        if year == 2022 and extracted_dir.exists():
            # Use the extracted monthly files for 2022 because
            # Python cannot read this archive's Deflate64 compression.
            csv_files = sorted(extracted_dir.glob("*.csv"))

            if not csv_files:
                raise FileNotFoundError(
                    f"No extracted CSV files found in {extracted_dir}"
                )

            print(f"\nProcessing extracted monthly files for {year}...")

            for csv_file in csv_files:
                print(f"\nReading {csv_file.name}")
                process_csv_stream(csv_file, writer_holder)

        elif zip_path.exists():
            print(f"\nProcessing monthly files for {year}...")

            with ZipFile(zip_path, "r") as archive:
                csv_names = sorted(
                    name
                    for name in archive.namelist()
                    if name.lower().endswith(".csv")
                )

                if not csv_names:
                    raise ValueError(f"No CSV files found in {zip_path}")

                for csv_name in csv_names:
                    print(f"\nReading {csv_name}")

                    with archive.open(csv_name) as csv_file:
                        process_csv_stream(csv_file, writer_holder)

        elif csv_path.exists():
            print(f"\nProcessing annual CSV for {year}...")
            process_csv_stream(csv_path, writer_holder)

        else:
            raise FileNotFoundError(
                f"No source file found for {year}. "
                f"Expected {zip_path} or {csv_path}"
            )

        if writer_holder["rows"] == 0:
            raise ValueError(f"No data rows processed for {year}")

        print(f"\nFinished {year}")
        print(f"Total rows: {writer_holder['rows']:,}")
        print(f"Output: {output_path}")

    finally:
        if writer_holder["writer"] is not None:
            writer_holder["writer"].close()


if __name__ == "__main__":
    for year in YEARS_TO_PROCESS:
        process_year(year)