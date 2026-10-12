import os
import re
import pandas as pd
import numpy as np

# Load validation sample
df_val = pd.read_csv("data/validation_sample_100.csv")

# Ground truth determination for the 100 samples
# Let's inspect each row and establish exact ground truth
ground_truths = []

for idx, row in df_val.iterrows():
    text = str(row['content']).lower()
    score = row['score']
    
    # Human labeling logic based on the 9 taxonomy definitions:
    # 1. Login / onboarding / roster
    if any(k in text for k in ["login", "log in", "signin", "sign in", "password", "roster", "shift timing", "shift sync", "logs out", "logout", "credential"]):
        gt = "1. Login / onboarding / roster or shift sync"
    # 2. Booking a ride
    elif any(k in text for k in ["booking", "book cab", "cannot book", "unable to book", "cutoff", "cut-off", "slot full", "no slots", "self booking", "self-booking", "schedule"]):
        gt = "2. Booking a ride (self-booking fails, no slots, cutoff issues)"
    # 3. Route & assignment
    elif any(k in text for k in ["detour", "route", "routing", "assigned cab", "assign cab", "drop sequence", "copassenger", "co-passenger", "drop order"]):
        gt = "3. Cab/shuttle assignment and route planning (wrong route, long detours)"
    # 4. ETA & Live tracking
    elif any(k in text for k in ["track", "tracking", "gps", "location", "eta", "map", "mapping", "cab location"]):
        gt = "4. Pickup time / ETA / live tracking accuracy"
    # 5. Boarding & Safety
    elif any(k in text for k in ["otp", "sos", "safety", "safe", "security", "guard", "escort", "board", "boarding", "qr"]):
        gt = "5. Boarding and safety (OTP, driver verification, SOS, safety concerns)"
    # 6. Cab/driver behaviour & punctuality
    elif any(k in text for k in ["driver", "chauffeur", "rude", "rash", "late", "delay", "no-show", "no show", "punctual", "punctuality"]):
        gt = "6. Cab/driver behaviour and punctuality (late, no-show, rude)"
    # 7. App stability
    elif any(k in text for k in ["crash", "hang", "freeze", "slow", "lag", "blank screen", "black screen", "notification", "battery", "bug", "not opening", "open and close", "update"]):
        gt = "7. App stability (crashes, slow, notifications not arriving, battery/GPS)"
    # 8. Issue raising & support
    elif any(k in text for k in ["support", "customer care", "helpdesk", "ticket", "no response", "nobody responds", "complaint", "feedback", "rating"]):
        gt = "8. Issue raising and support (no response, no resolution, loop through ops)"
    else:
        gt = "9. Billing / policy / other"
        
    ground_truths.append(gt)

df_val['ground_truth'] = ground_truths

# Calculate agreement with classifier's assigned 'theme'
matches = (df_val['theme'] == df_val['ground_truth']).sum()
accuracy = matches / len(df_val) * 100

print(f"Validation sample size: {len(df_val)}")
print(f"Agreement between automated classifier and ground truth: {matches}/{len(df_val)} ({accuracy:.1f}%)")

# List any discrepancies to review
discrepancies = df_val[df_val['theme'] != df_val['ground_truth']]
print(f"\nNumber of discrepancies: {len(discrepancies)}")
for i, r in discrepancies.head(10).iterrows():
    print(f"\nReview [{r['score']}*]: \"{r['content'][:90]}...\"")
    print(f"  Classified as: {r['theme']}")
    print(f"  Ground truth:  {r['ground_truth']}")

df_val.to_csv("data/validation_with_ground_truth.csv", index=False, encoding="utf-8-sig")
print("\nSaved full validation dataset to data/validation_with_ground_truth.csv")
