import os
import re
import json
import pandas as pd
import numpy as np
from tune_and_validate import classify_text, THEMES

# Load data
df = pd.read_csv("data/classified_reviews.csv")
df['at'] = pd.to_datetime(df['at'])
if 'replied_at' in df.columns:
    df['replied_at'] = pd.to_datetime(df['replied_at'])

# Discover app details from step1
with open("step1_apps_discovery.json", "r", encoding="utf-8") as f:
    discovery = json.load(f)

app_meta = discovery.get("com.moveinsync.ets", {})
hist = app_meta.get("histogram", [7316, 839, 1224, 7253, 98242])
total_ratings = sum(hist)
total_stars = sum((i + 1) * count for i, count in enumerate(hist))
current_avg = total_stars / total_ratings

sample_counts = df['score'].value_counts().to_dict()

# Scaling factor per star: f_k = H_k / N_sample_k
scaling_factors = {}
for star in range(1, 6):
    h_k = hist[star - 1]
    n_k = sample_counts.get(star, 1)
    scaling_factors[star] = h_k / n_k

# -------------------------------------------------------------------------
# A) RATING-IMPACT RANKING
# -------------------------------------------------------------------------
low_stars = df[df['score'].isin([1, 2])].copy()
total_low_stars = len(low_stars)
total_helpful_votes_low = low_stars['thumbs_up_count'].sum()

themes_all = list(df['theme'].unique())
impact_records = []

for t in themes_all:
    t_df = df[df['theme'] == t]
    t_low = t_df[t_df['score'].isin([1, 2])]
    
    count_low = len(t_low)
    share_low = (count_low / total_low_stars) * 100 if total_low_stars > 0 else 0
    
    helpful_votes = t_low['thumbs_up_count'].sum()
    share_helpful = (helpful_votes / total_helpful_votes_low) * 100 if total_helpful_votes_low > 0 else 0
    
    delta_stars = 0.0
    for _, r in t_df[t_df['score'] < 4].iterrows():
        s = int(r['score'])
        gain = 4 - s
        delta_stars += gain * scaling_factors.get(s, 1.0)
        
    rating_gain = delta_stars / total_ratings
    simulated_rating = (total_stars + delta_stars) / total_ratings
    
    impact_records.append({
        "theme": t,
        "total_reviews": len(t_df),
        "low_star_reviews": count_low,
        "share_of_low_stars_pct": round(share_low, 2),
        "helpful_votes_low": int(helpful_votes),
        "share_of_helpful_votes_pct": round(share_helpful, 2),
        "delta_stars_scaled": round(delta_stars, 1),
        "simulated_rating_gain": round(rating_gain, 4),
        "simulated_new_rating": round(simulated_rating, 4)
    })

impact_df = pd.DataFrame(impact_records).sort_values(by="simulated_rating_gain", ascending=False)
print("\n=== THEME RATING-IMPACT RANKING ===")
print(impact_df[["theme", "low_star_reviews", "share_of_low_stars_pct", "share_of_helpful_votes_pct", "simulated_rating_gain", "simulated_new_rating"]].to_string(index=False))

# -------------------------------------------------------------------------
# B) TREND ANALYSIS & REGRESSION DETECTION
# -------------------------------------------------------------------------
df['year_month'] = df['at'].dt.to_period('M')
monthly = df.groupby('year_month').agg(
    total_reviews=('score', 'count'),
    avg_score=('score', 'mean'),
    low_star_count=('score', lambda s: (s <= 2).sum()),
).reset_index()
monthly['low_star_share_pct'] = (monthly['low_star_count'] / monthly['total_reviews']) * 100
monthly['year_month_str'] = monthly['year_month'].astype(str)

recent_monthly = monthly.tail(24)

# Version analysis
ver_df = df[df['review_created_version'].notna() & (df['review_created_version'].str.strip() != "")].copy()
version_agg = ver_df.groupby('review_created_version').agg(
    review_count=('score', 'count'),
    avg_score=('score', 'mean'),
    low_star_count=('score', lambda s: (s <= 2).sum()),
    first_date=('at', 'min'),
    last_date=('at', 'max')
).reset_index()
version_agg['low_star_share_pct'] = (version_agg['low_star_count'] / version_agg['review_count']) * 100
ver_sig = version_agg[version_agg['review_count'] >= 50].sort_values(by="last_date", ascending=False).copy()
ver_sig['first_date'] = ver_sig['first_date'].astype(str)
ver_sig['last_date'] = ver_sig['last_date'].astype(str)

# Check 12.19.0 regression specifically
v1219 = df[df['review_created_version'] == '12.19.0']
v1218 = df[df['review_created_version'] == '12.18.0']
print(f"\nVersion 12.19.0: N={len(v1219)}, Avg Score={v1219['score'].mean():.2f}, 1-2 star %={(v1219['score']<=2).mean()*100:.1f}%")
print(f"Version 12.18.0: N={len(v1218)}, Avg Score={v1218['score'].mean():.2f}, 1-2 star %={(v1218['score']<=2).mean()*100:.1f}%")
print("\nTop themes in v12.19.0 (1-2 stars):")
print(v1219[v1219['score'] <= 2]['theme'].value_counts())

# -------------------------------------------------------------------------
# C) INTERCEPT ANALYSIS
# -------------------------------------------------------------------------
intercept_patterns = [
    r"\b(no response|nobody response|nobody responds|no one responds|nobody replies|no reply)\b",
    r"\b(no support|worst support|useless support|pathetic support|customer care|helpdesk|support team)\b",
    r"\b(ticket|tickets|complaint registered|raised (a |the )?complaint|writing emails|sent emails)\b",
    r"\b(transport desk|loop through ops|no resolution|closed without resolution)\b",
    r"\b(forcing .* rating|rate after every ride|no skip option)\b"
]

def check_intercept(text):
    if not isinstance(text, str):
        return False
    t = text.lower()
    return any(re.search(p, t) for p in intercept_patterns)

df['is_intercept_candidate'] = df['content'].apply(check_intercept)
intercept_low = df[(df['score'].isin([1, 2])) & (df['is_intercept_candidate'])]
intercept_total_low = len(df[df['score'].isin([1, 2])])
intercept_pct = (len(intercept_low) / intercept_total_low) * 100

print(f"\n=== INTERCEPT ANALYSIS ===")
print(f"Total 1-2 star reviews: {intercept_total_low}")
print(f"1-2 star reviews indicating in-app support failure / forced feedback: {len(intercept_low)} ({intercept_pct:.2f}%)")

# -------------------------------------------------------------------------
# D) DEVELOPER RESPONSE ANALYSIS
# -------------------------------------------------------------------------
has_reply = df['reply_content'].notna()
overall_reply_rate = has_reply.mean() * 100
low_star_reply_rate = df[df['score'].isin([1, 2])]['reply_content'].notna().mean() * 100
high_star_reply_rate = df[df['score'] >= 4]['reply_content'].notna().mean() * 100

df_replied = df[has_reply].copy()
df_replied['reply_delay_days'] = (df_replied['replied_at'] - df_replied['at']).dt.total_seconds() / 86400.0

avg_reply_time = df_replied['reply_delay_days'].median()

generic_patterns = [
    r"(regret the inconvenience|inconvenience caused)",
    r"(write to us at|email us at|reach out to us at|support@moveinsync\.com)",
    r"(thank you for (your )?(valuable )?feedback)",
    r"(glad to know you had a great experience)"
]
generic_replies = df_replied['reply_content'].apply(lambda x: sum(bool(re.search(p, str(x).lower())) for p in generic_patterns))
generic_reply_pct = (generic_replies >= 1).mean() * 100

print(f"\n=== DEVELOPER RESPONSE ANALYSIS ===")
print(f"Overall Reply Rate: {overall_reply_rate:.2f}%")
print(f"Reply Rate on 1-2 Stars: {low_star_reply_rate:.2f}%")
print(f"Reply Rate on 4-5 Stars: {high_star_reply_rate:.2f}%")
print(f"Median Reply Time: {avg_reply_time:.1f} days")
print(f"Generic / Templated Reply Share: {generic_reply_pct:.2f}%")

# -------------------------------------------------------------------------
# E) PRODUCT BUG VS OPS / POLICY / UNCLEAR
# -------------------------------------------------------------------------
owner_counts = low_stars['root_cause_owner'].value_counts()
owner_pcts = low_stars['root_cause_owner'].value_counts(normalize=True) * 100
owner_summary = pd.DataFrame({'Count': owner_counts, 'Share (%)': owner_pcts.round(2)})

# -------------------------------------------------------------------------
# F) PEER BENCHMARK
# -------------------------------------------------------------------------
peer_safetrax = pd.read_csv("data/peer_safetrax_reviews.csv")
peer_routematic = pd.read_csv("data/peer_routematic_reviews.csv")

def classify_peer_df(peer_df):
    themes = []
    for _, row in peer_df.iterrows():
        t_idx, _, _, _ = classify_text(row.get('content'), row.get('score'))
        themes.append(THEMES[t_idx - 1])
    peer_df['theme'] = themes
    return peer_df

peer_safetrax = classify_peer_df(peer_safetrax)
peer_routematic = classify_peer_df(peer_routematic)

peer_bench = pd.DataFrame({
    'MoveInSync': (low_stars['theme'].value_counts(normalize=True) * 100).round(2),
    'Safetrax': (peer_safetrax[peer_safetrax['score'].isin([1, 2])]['theme'].value_counts(normalize=True) * 100).round(2),
    'Routematic': (peer_routematic[peer_routematic['score'].isin([1, 2])]['theme'].value_counts(normalize=True) * 100).round(2),
}).fillna(0)

print("\n=== PEER BENCHMARK: 1-2 STAR REVIEWS THEME DISTRIBUTION (%) ===")
print(peer_bench)

# Save JSON results
analysis_results = {
    "app_id": "com.moveinsync.ets",
    "total_ratings": total_ratings,
    "current_rating": round(current_avg, 4),
    "histogram": hist,
    "total_scraped_reviews": len(df),
    "impact_table": impact_df.to_dict(orient="records"),
    "recent_monthly": recent_monthly[["year_month_str", "total_reviews", "avg_score", "low_star_share_pct"]].to_dict(orient="records"),
    "versions": ver_sig.head(20).to_dict(orient="records"),
    "intercept": {
        "low_star_count": intercept_total_low,
        "intercept_count": len(intercept_low),
        "intercept_pct": round(intercept_pct, 2)
    },
    "developer_response": {
        "overall_reply_rate": round(overall_reply_rate, 2),
        "low_star_reply_rate": round(low_star_reply_rate, 2),
        "high_star_reply_rate": round(high_star_reply_rate, 2),
        "median_reply_delay_days": round(avg_reply_time, 1),
        "templated_reply_pct": round(generic_reply_pct, 2)
    },
    "root_cause_ownership": owner_summary.to_dict(),
    "peer_benchmark": peer_bench.to_dict()
}

with open("data/analysis_results.json", "w", encoding="utf-8") as f:
    json.dump(analysis_results, f, indent=2)

print("\nSaved comprehensive analysis results to data/analysis_results.json")
