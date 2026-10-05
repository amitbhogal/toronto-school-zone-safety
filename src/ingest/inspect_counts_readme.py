
from pathlib import Path
import pandas as pd

file_path = Path("data/raw/stationary-detail-counts-readme.xlsx")

excel_file = pd.ExcelFile(file_path)

print("Sheets found:")
print(excel_file.sheet_names)

for sheet_name in excel_file.sheet_names:
    print(f"\n--- Sheet: {sheet_name} ---")
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    print(df.to_string(index=False, header=False))