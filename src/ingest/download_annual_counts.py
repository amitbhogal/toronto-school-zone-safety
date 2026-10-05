from pathlib import Path
import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

URLS = {
    2023: "https://opendata.toronto.ca/transportation.services/school-safety-zone-watch-your-speed-program-detailed-speed-counts/stationary-2023.csv",
    2024: "https://opendata.toronto.ca/transportation.services/school-safety-zone-watch-your-speed-program-detailed-speed-counts/stationary-2024.csv",
    2025: "https://opendata.toronto.ca/transportation.services/school-safety-zone-watch-your-speed-program-detailed-speed-counts/stationary-2025.csv",
}

for year, url in URLS.items():
    output_path = RAW_DIR / f"stationary-{year}.csv"

    if output_path.exists():
        print(f"{year}: already exists, skipping")
        continue

    print(f"\nDownloading {year}...")
    print(f"URL: {url}")

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with output_path.open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    print(f"Saved: {output_path}")