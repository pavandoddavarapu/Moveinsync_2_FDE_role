import json
from google_play_scraper import app, search

known_packages = [
    "com.moveinsync.ets",              # Primary Employee App
    "com.moveinsync.driver.dco",          # Driver Partner
    "com.moveinsync.driver.lite",         # Partner Lite
    "field.moveinsync.ets",              # Field app
]

# Let's inspect com.moveinsync.ets and find developer ID to see all apps by developer
results = {}
for pkg in known_packages:
    try:
        data = app(pkg, lang="en", country="in")
        results[pkg] = {
            "title": data.get("title"),
            "appId": data.get("appId"),
            "developer": data.get("developer"),
            "developerId": data.get("developerId"),
            "score": data.get("score"),
            "ratings": data.get("ratings"),
            "reviews": data.get("reviews"),
            "histogram": data.get("histogram"),
            "installs": data.get("installs"),
            "minInstalls": data.get("minInstalls"),
            "genre": data.get("genre"),
            "version": data.get("version"),
            "updated": data.get("updated"),
            "url": data.get("url")
        }
        print(f"Loaded: {data.get('title')} ({pkg}) - Rating: {data.get('score')} ({data.get('ratings')} ratings, {data.get('reviews')} reviews, {data.get('installs')} installs)")
    except Exception as e:
        print(f"Error for {pkg}: {e}")

# Also search developer name if available
if "com.moveinsync.ets" in results:
    dev_id = results["com.moveinsync.ets"].get("developerId")
    dev_name = results["com.moveinsync.ets"].get("developer")
    print(f"\nDeveloper Name: {dev_name}, Developer ID: {dev_id}")
    # search more terms
    for query in ["MoveInSync Technology Solutions", "MoveInSync Shuttle", "MoveInSync WorkInSync"]:
        try:
            extra = search(query, lang="en", country="in")
            for item in extra:
                if item['appId'] and item['appId'] not in results and ("moveinsync" in item['appId'].lower() or "workinsync" in item['appId'].lower()):
                    try:
                        d = app(item['appId'], lang="en", country="in")
                        results[item['appId']] = {
                            "title": d.get("title"),
                            "appId": d.get("appId"),
                            "developer": d.get("developer"),
                            "score": d.get("score"),
                            "ratings": d.get("ratings"),
                            "reviews": d.get("reviews"),
                            "histogram": d.get("histogram"),
                            "installs": d.get("installs"),
                            "version": d.get("version")
                        }
                        print(f"Found related app: {d.get('title')} ({item['appId']}) - Rating: {d.get('score')}")
                    except Exception as err:
                        pass
        except Exception as e:
            pass

with open("step1_apps_discovery.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nDiscovery completed successfully. Saved to step1_apps_discovery.json")
