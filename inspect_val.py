import pandas as pd
import json

df = pd.read_csv("data/validation_sample_100.csv")

# Let's inspect each row in detail and write human-verified labels
verified_labels = []

for idx, row in df.iterrows():
    text = str(row['content']).strip()
    score = row['score']
    
    # We will print out and classify with rigorous domain understanding:
    # 1. Login / onboarding / roster: registration, corporate login, password, roster, shift sync, email verification
    # 2. Booking a ride: booking slots, self-booking, cutoff, waitlist, cancel booking, scheduling
    # 3. Route & assignment: long routes, detours, cab allocation, copassenger, drop sequence
    # 4. ETA & Live tracking: tracking, map location, GPS, ETA, cab not moving
    # 5. Boarding & safety: trip OTP, driver verification mismatch, SOS, physical safety, escort guard
    # 6. Cab/driver behaviour & punctuality: driver rude, rash driving, cab delay/late, no-show, driver cancellation, AC off
    # 7. App stability: crashes, freeze, slow app, notifications, battery drain, update broke app
    # 8. Issue raising & support: transport desk, customer support, emails ignored, tickets, forced rating prompt
    # 9. Billing / policy / other: billing, deductions, company transport policy, or generic praise/criticism
    pass

print(f"Total validation samples: {len(df)}")
