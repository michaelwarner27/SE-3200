"""One-off script: download country-name lists from restcountries.com into static/data/.

Run it once (the free plan allows at most 100 results per call, so each list is
fetched page by page):

    RESTCOUNTRIES_KEY=rc_live_xxx python3 tools/build_country_lists.py

Writes static/data/countries/<list>.json (a sorted JSON array of common names) and
static/data/countries/index.json (the list ids and labels used by the page).
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.restcountries.com/countries/v5"
OUT = Path(__file__).resolve().parent.parent / "static" / "data" / "countries"
PAGE = 100  # free-plan maximum
CONTINENTS = ["Africa", "Antarctica", "Asia", "Europe", "North America", "Oceania", "South America"]

# id -> (label, path under BASE, extra query params)
LISTS = {
    "all": ("All countries", "", {}),
    "un": ("UN members", "", {"memberships.un": "1"}),
}
for name in CONTINENTS:
    LISTS[name.lower().replace(" ", "-")] = (name, "/continents/" + urllib.parse.quote(name), {})


def fetch_names(path, params, key):
    names, offset = [], 0
    while True:
        query = {"limit": PAGE, "offset": offset, "response_fields": "names.common", **params}
        request = urllib.request.Request(
            f"{BASE}{path}?{urllib.parse.urlencode(query)}",
            headers={"Authorization": f"Bearer {key}", "User-Agent": "country-guesser-list-builder"},
        )
        with urllib.request.urlopen(request) as response:
            data = json.load(response)["data"]
        names += [obj["names"]["common"] for obj in data["objects"]]
        if not data["meta"]["more"]:
            return sorted(set(names))
        offset += PAGE
        time.sleep(0.5)  # stay well under the rate limit


def main():
    key = os.environ.get("RESTCOUNTRIES_KEY")
    if not key:
        sys.exit("Set RESTCOUNTRIES_KEY to your restcountries.com API key.")
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for list_id, (label, path, params) in LISTS.items():
        names = fetch_names(path, params, key)
        (OUT / f"{list_id}.json").write_text(json.dumps(names, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        index.append({"id": list_id, "label": label, "count": len(names)})
        print(f"{label}: {len(names)} countries")
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
