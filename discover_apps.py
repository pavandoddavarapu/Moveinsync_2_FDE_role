import json
from google_play_scraper import search, app

results = search("MoveInSync", lang="en", country="in")
print(f"Found {len(results)} search results:")
apps_info = []
for res in results:
    app_id = res['appId']
    title = res['title']
    print(f"- {title} ({app_id})")
    try:
        details = app(app_id, lang="en", country="in")
        info = {
            "title": details.get("title"),
            "appId": details.get("appId"),
            "developer": details.get("developer"),
            "score": details.get("score"),
            "ratings": details.get("ratings"),
            "reviews": details.get("reviews"),
            "histogram": details.get("histogram"),
            "installs": details.get("installs"),
            "minInstalls": details.get("minInstalls"),
            "genre": details.get("genre"),
            "summary": details.get("summary"),
            "version": details.get("version"),
            "updated": details.get("updated")
        }
        apps_info.append(info)
    except Exception as e:
        print(f"  Error fetching details for {app_id}: {e}")

with open("data_apps_discovery.json", "w", encoding="utf-8") as f:
    json.dump(apps_info, f, indent=2)

print("\nSaved app discovery to data_apps_discovery.json")
