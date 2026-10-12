import sys
import re
import os
import json
import pandas as pd
import numpy as np

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

THEMES = [
    "1. Login / onboarding / roster or shift sync",
    "2. Booking a ride (self-booking fails, no slots, cutoff issues)",
    "3. Cab/shuttle assignment and route planning (wrong route, long detours)",
    "4. Pickup time / ETA / live tracking accuracy",
    "5. Boarding and safety (OTP, driver verification, SOS, safety concerns)",
    "6. Cab/driver behaviour and punctuality (late, no-show, rude)",
    "7. App stability (crashes, slow, notifications not arriving, battery/GPS)",
    "8. Issue raising and support (no response, no resolution, loop through ops)",
    "9. Billing / policy / other"
]

PATTERNS = {
    # 1. Login / onboarding / roster
    1: [
        r"\b(login|log in|logging in|logged in|sign in|signin|signing in|relogin|re-login)\b",
        r"\b(password|credential|credentials|user id|userid|corp id|corporate id|emp id|employee id)\b",
        r"\b(roster|rostering|shift sync|shift timing|shift time|shift change|schedule not (showing|reflecting|synced))\b",
        r"\b(registration|register|account locked|session expired|logs? out|logging out|auto logout|automatically logout)\b",
        r"\b(sso|authentication|auth fail)\b"
    ],
    # 2. Booking a ride
    2: [
        r"\b(book|booking|booked|self-booking|self booking|adhoc|ad-hoc)\b",
        r"\b(cutoff|cut-off|cut off|booking window|booking slot|slot full|no slots?|seat booking|reserve seat)\b",
        r"\b(unable to book|cannot book|can't book|booking fail(ed)?|failed to book|cancel booking|schedule|scheduling)\b",
        r"\b(waitlist|waitlisted|unable to schedule|cab not available|no cab available)\b"
    ],
    # 3. Route & assignment
    3: [
        r"\b(route|routing|routed|detour|detours|roundabout|circuitous)\b",
        r"\b(assign(ing|ment|ed)? cab|assign(ing|ment|ed)?|shuttle route|drop order|drop sequence|pickup sequence|first pickup last drop)\b",
        r"\b(wrong route|longest route|unnecessary (km|kms|distance|detour)|travel time too long|longer route)\b",
        r"\b(waypoint|dropped far|drop point|pickup point wrong|reach office very late due to route|routing logic)\b"
    ],
    # 4. ETA & Live tracking
    4: [
        r"\b(tracking|live tracking|real-time tracking|track cab|track my cab|track(ing)? the location|track the van)\b",
        r"\b(eta|estimated time|arrival time|pickup time wrong|wrong eta)\b",
        r"\b(map|mapping|google map|gps tracking|cab location|shows cab (at|in)|cab not moving|car not moving|stuck on map)\b",
        r"\b(location inaccurate|wrong location|fake location|reached but showing|shows reached|shows arrived)\b"
    ],
    # 5. Boarding & Safety
    5: [
        r"\b(otp|boarding otp|start otp|end otp|reach otp|trip otp)\b",
        r"\b(sos|safety|unsafe|security|security guard|escort|female safety|night travel|night shift safety)\b",
        r"\b(driver verification|vehicle number mismatch|different cab|different driver|unverified driver|wrong cab arrived)\b",
        r"\b(board|boarded|boarding pass|qr code|scan qr)\b"
    ],
    # 6. Cab/driver behaviour & punctuality
    6: [
        r"\b(driver|cab driver|driver's|drivers|chauffeur)\b",
        r"\b(rude|arrogant|misbehav(ed|iour|ior)|harsh|shouted|yelled|abusive|bad attitude|behavior|behaviour)\b",
        r"\b(late|delay|delayed|punctual|punctuality|not on time|came late|waiting for cab|reach late)\b",
        r"\b(no[- ]?show|didn't come|didn't show up|never arrived|cab not arrived|driver cancelled|ride cancelled by driver)\b",
        r"\b(rash driving|reckless|overspeeding|speeding|ac off|ac not working|switched off ac|asked for money|asked for tip|toll)\b"
    ],
    # 7. App stability
    7: [
        r"\b(crash|crashes|crashing|crashed|force close|keeps stopping|stopped working|closes as soon as|open and close)\b",
        r"\b(hang|hangs|hanging|freeze|freezes|frozen|blank screen|white screen|black screen)\b",
        r"\b(slow|sluggish|lag|lagging|loading issue|stuck on loading|spinning|keeps loading)\b",
        r"\b(notification|notifications|alert|push notification|battery drain|drains battery|battery consumption)\b",
        r"\b(bug|buggy|glitch|glitches|app not opening|not open|fails to open|won't open|wont open|server error|network error|uninstall and reinstall|reinstall)\b",
        r"\b(after update|new update|update made it worse|update is worse|since the update|bad update)\b"
    ],
    # 8. Issue raising & support
    8: [
        r"\b(support|customer care|customer support|helpdesk|help desk|ticket|tickets|grievance|helpline)\b",
        r"\b(transport desk|desk team|ops team|operations team|loop through ops)\b",
        r"\b(no response|no reply|nobody responds|no one responds|nobody replies|unresponsive|no resolution)\b",
        r"\b(useless support|pathetic support|worst support|complaint not resolved|ticket closed without resolution)\b",
        r"\b(no one to contact|call center|helpline not reachable|escalat(e|ed|ion)|feedback (box|form|option)|in-app feedback|cant submit feedback)\b",
        r"\b(forcing .* rating|force .* rating|rate after every ride|no skip option)\b"
    ],
    # 9. Billing / policy / other
    9: [
        r"\b(bill|billing|charged|charge|fare|payment|deduction|salary deduction|salary cut|reimbursement)\b",
        r"\b(policy|company policy|hr policy|transport policy|fine|penalty)\b"
    ]
}

def classify_single_review(text, score):
    if not isinstance(text, str) or not text.strip():
        sentiment = "Positive" if score >= 4 else ("Neutral" if score == 3 else "Negative")
        severity = "Low" if score >= 3 else ("Medium" if score == 2 else "High")
        return 9, sentiment, severity, "Unclear"

    text_lower = text.lower()

    # Determine sentiment
    if score >= 4:
        sentiment = "Positive"
    elif score == 3:
        neg_cues = ["but", "however", "bad", "slow", "worst", "issue", "problem", "improve", "fix", "delay"]
        sentiment = "Negative" if any(c in text_lower for c in neg_cues) else "Neutral"
    else:
        sentiment = "Negative"

    # Match themes
    scores_per_theme = {i: 0 for i in range(1, 10)}
    for theme_idx, pattern_list in PATTERNS.items():
        for pat in pattern_list:
            matches = re.findall(pat, text_lower)
            if matches:
                scores_per_theme[theme_idx] += len(matches) * 2

    # Disambiguation & priority weighting
    if re.search(r"\b(nobody responds|no support|pathetic support|customer care|ticket closed|transport desk)\b", text_lower):
        scores_per_theme[8] += 4

    # Forced rating prompt issue
    if re.search(r"\b(forcing .* rating|force .* rating|rate after every ride|no skip option)\b", text_lower):
        scores_per_theme[8] += 5

    # Login vs Boarding OTP
    if re.search(r"\b(login otp|otp for login|not able to login|unable to login|cant login|login issue)\b", text_lower):
        scores_per_theme[1] += 5
        if not re.search(r"\b(start trip|end trip|boarding otp|cab otp)\b", text_lower):
            scores_per_theme[5] = 0

    if re.search(r"\b(boarding otp|start otp|trip otp|driver asking otp|otp to start|otp for cab)\b", text_lower):
        scores_per_theme[5] += 5

    # App crash / won't open / update broke
    if re.search(r"\b(crash|freez|blank screen|won't open|wont open|closes as soon as|not opening|uninstall and reinstall)\b", text_lower):
        scores_per_theme[7] += 4

    # Live tracking / map
    if re.search(r"\b(live tracking|tracking not working|cab location|eta wrong|shows cab|gps tracking|track the location|worst mapping)\b", text_lower):
        scores_per_theme[4] += 4

    # Booking & cutoff
    if re.search(r"\b(cutoff|slot full|no slots|self-booking|booking fail|cannot book|unable to book|unable to schedule)\b", text_lower):
        scores_per_theme[2] += 4

    # Cab assignment
    if re.search(r"\b(not assigning cabs|cab not assigned|cab assignment|no cab assigned)\b", text_lower):
        scores_per_theme[3] += 4

    # Driver behaviour
    if re.search(r"\b(rude driver|driver rude|driver misbehav|driver cancelled|rash driving|driver no show|driver didn't come)\b", text_lower):
        scores_per_theme[6] += 4

    best_theme = max(scores_per_theme, key=scores_per_theme.get)
    if scores_per_theme[best_theme] == 0:
        best_theme = 9

    # Determine Severity
    high_sev_words = ["stranded", "safety", "emergency", "sos", "night", "danger", "abusive", "harass", "threat", "missed", "escalat", "fraud", "worst ever", "unusable", "uninstalled", "loss", "forced"]
    if score == 1 and (best_theme in [5, 6, 8, 7] or any(w in text_lower for w in high_sev_words)):
        severity = "High"
    elif score in [1, 2]:
        severity = "High" if any(w in text_lower for w in high_sev_words) else "Medium"
    elif score == 3:
        severity = "Medium" if any(w in text_lower for w in ["issue", "problem", "delay", "bug"]) else "Low"
    else:
        severity = "Low"

    # Determine Root-cause Owner
    owner = "Unclear"
    if best_theme in [4, 7]:
        owner = "Product bug"
    elif best_theme == 6:
        owner = "Ops-vendor behaviour"
    elif best_theme == 1:
        if re.search(r"\b(roster|shift|hr|admin|company|policy|not updated)\b", text_lower):
            owner = "Customer company policy"
        else:
            owner = "Product bug"
    elif best_theme == 2:
        if re.search(r"\b(cutoff|cut off|policy|rule|quota|limit|company|hr)\b", text_lower):
            owner = "Customer company policy"
        else:
            owner = "Product bug"
    elif best_theme == 3:
        if re.search(r"\b(algorithm|app|system|route logic|map)\b", text_lower):
            owner = "Product bug"
        else:
            owner = "Ops-vendor behaviour"
    elif best_theme == 5:
        if re.search(r"\b(otp not received|sms|app|server)\b", text_lower):
            owner = "Product bug"
        else:
            owner = "Ops-vendor behaviour"
    elif best_theme == 8:
        owner = "Ops-vendor behaviour" if "ops" in text_lower or "transport desk" in text_lower else "Product bug"
    elif best_theme == 9:
        if re.search(r"\b(policy|deduction|salary|rule)\b", text_lower):
            owner = "Customer company policy"
        else:
            owner = "Unclear"

    if scores_per_theme[best_theme] == 0:
        owner = "Unclear"

    return best_theme, sentiment, severity, owner

def main():
    raw_path = os.path.join("data", "raw_reviews.csv")
    print(f"Loading raw reviews from {raw_path}...")
    df = pd.read_csv(raw_path)
    print(f"Loaded {len(df)} reviews.")

    themes_assigned = []
    sentiments = []
    severities = []
    owners = []

    for idx, row in df.iterrows():
        t_idx, sent, sev, own = classify_single_review(row.get("content"), row.get("score"))
        themes_assigned.append(THEMES[t_idx - 1])
        sentiments.append(sent)
        severities.append(sev)
        owners.append(own)

    df["theme"] = themes_assigned
    df["sentiment"] = sentiments
    df["severity"] = severities
    df["root_cause_owner"] = owners

    out_classified = os.path.join("data", "classified_reviews.csv")
    df.to_csv(out_classified, index=False, encoding="utf-8-sig")
    print(f"Successfully saved classified reviews to {out_classified}")

    # Create validation sample
    np.random.seed(42)
    df_with_text = df[df["content"].notna() & (df["content"].str.strip().str.len() > 15)].copy()
    val_sample = df_with_text.sample(n=100, random_state=42).copy()
    val_path = os.path.join("data", "validation_sample_100.csv")
    val_sample.to_csv(val_path, index=False, encoding="utf-8-sig")
    print(f"Saved 100-sample validation dataset to {val_path}")

    print("\n--- Summary by Theme across all reviews ---")
    print(df["theme"].value_counts())
    print("\n--- Summary by Theme (1-2 star reviews) ---")
    low_stars = df[df["score"].isin([1, 2])]
    print(low_stars["theme"].value_counts())
    print("\n--- Summary by Root Cause Owner (1-2 star reviews) ---")
    print(low_stars["root_cause_owner"].value_counts())

if __name__ == "__main__":
    main()
