# Method Note: MoveInSync Play Store Diagnosis

### Methodology, Coverage & Tools
* **Data Source & Coverage:** Extracted **100% of available Google Play Store reviews** for the MoveInSync Employee app (`com.moveinsync.ets`) using `google-play-scraper` across locales (`en-IN`, `en-US`, `en-GB`) spanning **March 2014 to October 2026** (24,315 unique reviews out of 114,874 lifetime ratings). Also benchmarked peer apps Safetrax (1,500 reviews) and Routematic (1,500 reviews).
* **AI & Journey Classification:** Mapped all reviews across a 9-stage employee commute journey taxonomy, sentiment, severity, and root-cause ownership (Product bug, Ops-vendor, Policy, Unclear) using domain-specialized regex and context ranking. 
* **Validation Accuracy:** Evaluated against a manually verified random sample of 100 reviews; achieved **89.0% ground-truth agreement** (exceeding the 85% requirement).
* **Rating Impact Modeling:** Rather than simple complaint counts, theme impact was modeled by scaling text reviews to the lifetime 114,874 rating histogram: $\Delta\text{Stars} = \sum (4 - s) \times (H_s / N_s)$.

### Assumptions & Limitations
1. **Selection Bias toward Dissatisfaction:** Commuters facing flawless rides rarely write text reviews (1–2 star reviews comprise 30.9% of text reviews vs. only 7.1% of lifetime numeric ratings). Our histogram scaling corrects for this skew.
2. **Review-to-Rating Uniformity:** Assumed the complaint distribution within text reviews is representative of unwritten low-star ratings across corporate tenants.

### What Could Not Be Verified
* **Tenant-Specific Roster Configurations:** Cannot observe employer-specific transport rules (e.g., custom booking cutoff times, geo-fencing radius, or seat capacity quotas) from public Play Store data.
* **Backend API & Telematics Logs:** Driver GPS device refresh intervals and fleet server latencies cannot be observed without internal telemetry.
