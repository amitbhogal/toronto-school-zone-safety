
from pathlib import Path
import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

ARCHIVES = {
    2018: "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/d7522ce7-68b1-4f93-991a-0eb2f9ec7de5/resource/e622a992-6df5-443a-a1b5-25966475ddde/download/stationary_detailed_2018.zip",
    2019: "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/d7522ce7-68b1-4f93-991a-0eb2f9ec7de5/resource/da136e87-a85f-4b7b-aabd-404ac4762e4e/download/stationary_detailed_2019.zip",
    2020: "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/d7522ce7-68b1-4f93-991a-0eb2f9ec7de5/resource/0686ec8a-84e5-4012-a700-7a0358df2a29/download/stationary_detailed_2020.zip",
    2021: "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/d7522ce7-68b1-4f93-991a-0eb2f9ec7de5/resource/46747587-4112-4549-bd52-40808840ff21/download/stationary_detailed_2021.zip",
    2022: "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/d7522ce7-68b1-4f93-991a-0eb2f9ec7de5/resource/c120bb6f-c86e-4a60-84e7-c186f9ebc530/download/wys_stationary_detailed_2022.zip",
}

for year, url in ARCHIVES.items():
    output = RAW_DIR / f"stationary_detailed_{year}.zip"

    if output.exists():
        print(f"Already downloaded {year}; skipping.")
        continue

    print(f"\nDownloading {year}...")
    try:
        with requests.get(url, stream=True, timeout=(30, 300)) as response:
            response.raise_for_status()
            with output.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)

        print(f"Saved: {output} ({output.stat().st_size:,} bytes)")

    except Exception:
        if output.exists():
            output.unlink()
        raise

print("\nArchive downloads complete.")