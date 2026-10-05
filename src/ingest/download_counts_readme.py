
from pathlib import Path
import requests

url = (
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/"
    "dataset/d7522ce7-68b1-4f93-991a-0eb2f9ec7de5/"
    "resource/882f3782-3b99-48bc-bb95-afb52f40d6d7/"
    "download/stationary-detail-counts-readme.xlsx"
)

output = Path("data/raw/stationary-detail-counts-readme.xlsx")
output.parent.mkdir(parents=True, exist_ok=True)

response = requests.get(url, timeout=60)
response.raise_for_status()
output.write_bytes(response.content)

print(f"Downloaded: {output}")
print(f"File size: {len(response.content):,} bytes")