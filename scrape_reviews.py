import os
import time
import pandas as pd
from google_play_scraper import reviews, Sort, reviews_all

os.makedirs("data", exist_ok=True)
app_id = "com.moveinsync.ets"

print(f"Starting review scraping for {app_id}...")

all_reviews = []
seen_ids = set()

# Strategy 1: Attempt reviews_all for en/in
print("Attempting reviews_all (en, in)...")
try:
    revs = reviews_all(
        app_id,
        sleep_milliseconds=500,
        lang='en',
        country='in',
        sort=Sort.NEWEST
    )
    print(f"reviews_all returned {len(revs)} reviews.")
    for r in revs:
        if r['reviewId'] not in seen_ids:
            seen_ids.add(r['reviewId'])
            all_reviews.append(r)
except Exception as e:
    print(f"reviews_all encountered error or limit: {e}")

# Strategy 2: If reviews_all hits limits or stops, paginate with reviews() across Sort.NEWEST and Sort.MOST_RELEVANT, and multiple countries
countries = ['in', 'us', 'gb']
sorts = [Sort.NEWEST, Sort.MOST_RELEVANT]

for c in countries:
    for s in sorts:
        print(f"Scraping with country={c}, sort={s}...")
        continuation_token = None
        batch_count = 0
        while True:
            try:
                result, continuation_token = reviews(
                    app_id,
                    lang='en',
                    country=c,
                    sort=s,
                    count=200,
                    continuation_token=continuation_token
                )
                if not result:
                    break
                new_in_batch = 0
                for r in result:
                    if r['reviewId'] not in seen_ids:
                        seen_ids.add(r['reviewId'])
                        all_reviews.append(r)
                        new_in_batch += 1
                batch_count += 1
                print(f"  Batch {batch_count}: fetched {len(result)} reviews ({new_in_batch} new). Total unique: {len(all_reviews)}")
                if continuation_token is None or continuation_token.token is None:
                    break
                if new_in_batch == 0 and batch_count > 10:
                    # Stopping if no new reviews after repeated batches
                    break
                time.sleep(0.3)
            except Exception as e:
                print(f"  Error during pagination: {e}")
                break

print(f"\nTotal scraped unique reviews: {len(all_reviews)}")

# Convert to structured DataFrame
records = []
for r in all_reviews:
    records.append({
        "review_id": r.get("reviewId"),
        "user_name": r.get("userName"),
        "score": r.get("score"),
        "content": r.get("content"),
        "at": r.get("at"),
        "review_created_version": r.get("reviewCreatedVersion"),
        "app_version": r.get("appVersion"),
        "thumbs_up_count": r.get("thumbsUpCount"),
        "reply_content": r.get("replyContent"),
        "replied_at": r.get("repliedAt")
    })

df = pd.DataFrame(records)
# Sort by date descending
if not df.empty and "at" in df.columns:
    df["at"] = pd.to_datetime(df["at"])
    df = df.sort_values(by="at", ascending=False)

output_path = os.path.join("data", "raw_reviews.csv")
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"Saved {len(df)} raw reviews to {output_path}")

# Display brief stats
print("\nScore distribution in scraped sample:")
print(df["score"].value_counts().sort_index())
print(f"\nDate range: {df['at'].min()} to {df['at'].max()}")
print(f"Developer reply rate: {(df['reply_content'].notna().sum() / len(df) * 100):.2f}%")
