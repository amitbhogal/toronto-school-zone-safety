
from pathlib import Path
from zipfile import ZipFile
import pandas as pd

archive_path = Path("data/raw/stationary_detailed_2017.zip")
csv_name = "wys_stationary_detailed_201701.csv"

with ZipFile(archive_path, "r") as archive:
    with archive.open(csv_name) as csv_file:
        df = pd.read_csv(csv_file, nrows=5)

print("Columns:")
print(df.columns.tolist())

print("\nFirst five rows:")
print(df.to_string(index=False))

print("\nData types:")
print(df.dtypes)