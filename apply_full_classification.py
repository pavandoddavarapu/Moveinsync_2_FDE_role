import os
import pandas as pd
from tune_and_validate import classify_text, THEMES

raw_path = os.path.join("data", "raw_reviews.csv")
print(f"Reading raw reviews from {raw_path}...")
df = pd.read_csv(raw_path)

themes = []
sentiments = []
severities = []
owners = []

for idx, row in df.iterrows():
    t_idx, sent, sev, own = classify_text(row['content'], row['score'])
    themes.append(THEMES[t_idx - 1])
    sentiments.append(sent)
    severities.append(sev)
    owners.append(own)

df['theme'] = themes
df['sentiment'] = sentiments
df['severity'] = severities
df['root_cause_owner'] = owners

out_path = os.path.join("data", "classified_reviews.csv")
df.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"Saved {len(df)} classified reviews to {out_path}")

print("\n--- Summary of 1-2 star reviews by Theme ---")
low_stars = df[df['score'].isin([1, 2])]
print(low_stars['theme'].value_counts())
print("\n--- Summary of 1-2 star reviews by Root Cause Owner ---")
print(low_stars['root_cause_owner'].value_counts())
