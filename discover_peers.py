from google_play_scraper import search, app
import json

queries = ["Safetrax", "Routematic", "WhistleDrive"]
peers = {}
for q in queries:
    results = search(q, lang="en", country="in")
    for r in results[:3]:
        app_id = r['appId']
        if app_id:
            try:
                data = app(app_id, lang="en", country="in")
                peers[app_id] = {
                    "title": data.get("title"),
                    "appId": data.get("appId"),
                    "score": data.get("score"),
                    "ratings": data.get("ratings"),
                    "reviews": data.get("reviews"),
                    "histogram": data.get("histogram"),
                    "installs": data.get("installs"),
                }
                print(f"Peer: {data.get('title')} ({app_id}) - Rating: {data.get('score')} ({data.get('ratings')} ratings)")
            except Exception as e:
                pass

with open("peers_discovery.json", "w", encoding="utf-8") as f:
    json.dump(peers, f, indent=2)
