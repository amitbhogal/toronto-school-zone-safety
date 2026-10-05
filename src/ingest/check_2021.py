from pathlib import Path
from zipfile import ZipFile
import csv

project_root = Path(__file__).resolve().parents[2]
zip_path = project_root / "data" / "raw" / "stationary_detailed_2021.zip"

with ZipFile(zip_path) as archive:
    csv_files = sorted(
        name for name in archive.namelist()
        if name.lower().endswith(".csv")
    )

    for name in csv_files:
        with archive.open(name) as file:
            row_count = sum(1 for _ in csv.DictReader(
                (line.decode("utf-8-sig") for line in file)
            ))
        print(f"{name}: {row_count:,} data rows")