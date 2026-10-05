
from pathlib import Path
import requests

url = (
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/"
    "dataset/d7522ce7-68b1-4f93-991a-0eb2f9ec7de5/"
    "resource/61d91f4e-29c8-4bf7-aeb3-8c246444867b/"
    "download/stationary_detailed_2017.zip"
)

output = Path("data/raw/stationary_detailed_2017.zip")
output.parent.mkdir(parents=True, exist_ok=True)

print("Downloading 2017 data...")
response = requests.get(url, timeout=300)
response.raise_for_status()
output.write_bytes(response.content)

print(f"Downloaded: {output}")
print(f"File size: {len(response.content):,} bytes")