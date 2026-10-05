
import requests

dataset_id = (
    "school-safety-zone-watch-your-speed-program-detailed-speed-counts"
)

url = (
    "https://ckan0.cf.opendata.inter.prod-toronto.ca"
    "/api/3/action/package_show"
)

response = requests.get(
    url,
    params={"id": dataset_id},
    timeout=30,
)
response.raise_for_status()

dataset = response.json()["result"]

for resource in dataset["resources"]:
    name = resource.get("name", "")
    resource_url = resource.get("url", "")

    if "stationary" in name.lower():
        print(f"{name}")
        print(f"  URL: {resource_url}")