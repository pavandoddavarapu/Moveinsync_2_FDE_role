import os
import pandas as pd
from google_play_scraper import reviews, Sort

os.makedirs("data", exist_ok=True)

peers = {
    "safetrax": "in.mtap.iincube.safetrax.commuter",
    "routematic": "com.routematic.employee"
}

for name, pkg in peers.items():
    print(f"Scraping peer reviews for {name} ({pkg})...")
    revs, _ = reviews(
        pkg,
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=1500
    )
    df = pd.DataFrame(revs)
    out_file = os.path.join("data", f"peer_{name}_reviews.csv")
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} reviews to {out_file}")
