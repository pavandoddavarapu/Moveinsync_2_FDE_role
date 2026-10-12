import pandas as pd
import json

df = pd.read_csv("data/classified_reviews.csv")

themes_to_extract = [
    (4, 'Live Tracking & ETA Accuracy'),
    (7, 'App Stability & Crash on Launch/Update'),
    (2, 'Ride Booking, Cutoff & Slots'),
    (1, 'Login, Session Logout & Auth'),
    (8, 'In-App Support Intercept & Forced Rating'),
    (3, 'Route Assignment & Detours'),
    (6, 'Driver Punctuality & Behaviour')
]

results = {}

for t_idx, t_name in themes_to_extract:
    sub = df[(df['score'].isin([1, 2])) & (df['theme'].str.startswith(str(t_idx))) & (df['content'].str.len() > 30)].sort_values(by='thumbs_up_count', ascending=False)
    excerpts = []
    for _, r in sub.head(4).iterrows():
        excerpts.append({
            "review_id": str(r['review_id']),
            "version": str(r.get('review_created_version')),
            "score": int(r['score']),
            "thumbs_up": int(r.get('thumbs_up_count', 0)),
            "date": str(r['at']),
            "text": str(r['content']).strip()
        })
    results[t_name] = excerpts

with open("data/excerpts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

for t_name, excs in results.items():
    print(f"\n==================== {t_name} ====================")
    for e in excs[:3]:
        print(f"[{e['score']}* | v{e['version']} | ThumbsUp: {e['thumbs_up']} | ID: {e['review_id']}]")
        print(f"\"{e['text']}\"\n")
