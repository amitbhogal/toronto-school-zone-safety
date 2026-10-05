from pathlib import Path

import requests


API_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"

DATASET_ID = "school-safety-zone-watch-your-speed-program-locations"

OUTPUT_FILE = Path("data/raw/watch_your_speed_locations.csv")


def get_dataset():
    response = requests.get(
        API_URL,
        params={"id": DATASET_ID},
    )

    response.raise_for_status()

    return response.json()["result"]


def find_location_resource(dataset):
    for resource in dataset["resources"]:
        if resource["name"] == "School Safety Zone Watch Your Speed Program - Locations":
            return resource

    raise ValueError("Watch Your Speed location resource not found")


def download_resource(resource):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(resource["url"])
    response.raise_for_status()

    OUTPUT_FILE.write_bytes(response.content)

    print(f"Downloaded: {OUTPUT_FILE}")
    print(f"Size: {len(response.content):,} bytes")


dataset = get_dataset()

resource = find_location_resource(dataset)

print("Resource found:")
print(resource["name"])
print(resource["format"])
print(resource["url"])

download_resource(resource)