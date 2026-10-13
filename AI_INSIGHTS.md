# AI Insights - RFM Customer Segmentation

*Auto-generated from 1,500 customers and 17,021 transactions (reference date 2026-10-13).*

## Executive summary

This store earned INR 494.7L in the last year. The single biggest revenue driver is the **Champions** segment: 343 customers (23%) contributing INR 308.7L (62% of revenue). 
The **Champions** group is small (343 customers) but punches far above its weight with INR 308.7L (62% of revenue) - retention here is the highest-ROI activity in the business. 
On the other side, 600 customers (40%) sit in the At Risk / Can't Lose Them / Hibernating / Lost buckets, representing INR 20.1L of past-year revenue that is cooling or gone - this is where win-back campaigns earn their keep.

## Segment profiles and recommended actions

### Champions - 343 customers, INR 308.7L (62%)

- Typical behaviour: last order ~25 days ago, ~27.6 orders/year.

- **Action: Reward and retain.** Early access to launches, loyalty points, referral bonuses - these customers are your best advocates.

### Loyal Customers - 447 customers, INR 160.2L (32%)

- Typical behaviour: last order ~110 days ago, ~13.3 orders/year.

- **Action: Keep the habit.** Subscription-style nudges, cross-sell bundles, thank-you perks so they never drift.

### Lost - 492 customers, INR 10.0L (2%)

- Typical behaviour: last order ~304 days ago, ~1.6 orders/year.

- **Action: Let go (for now).** Suppress from paid campaigns; keep in a cheap newsletter pool in case they return on their own.

### At Risk - 74 customers, INR 7.3L (1%)

- Typical behaviour: last order ~286 days ago, ~4.6 orders/year.

- **Action: Win back soon.** Time-limited 'we miss you' offer on previously bought categories; the window closes fast from here.

### Potential Loyalists - 57 customers, INR 3.0L (1%)

- Typical behaviour: last order ~14 days ago, ~3.2 orders/year.

- **Action: Convert to loyal.** Targeted offers on their second favourite category; ask for reviews to deepen the tie.

### Hibernating - 34 customers, INR 2.8L (1%)

- Typical behaviour: last order ~284 days ago, ~2.9 orders/year.

- **Action: Cheap reactivation.** Low-cost email/SMS with deep discounts; do not spend paid-media money on them.

### Needs Attention - 36 customers, INR 2.0L (0%)

- Typical behaviour: last order ~26 days ago, ~4.6 orders/year.

- **Action: Watch list.** Above-average but cooling; A/B test messaging before they slide into At Risk.

### About to Sleep - 17 customers, INR 0.8L (0%)

- Typical behaviour: last order ~217 days ago, ~2.4 orders/year.

- **Action: Wake-up nudge.** Reminder of loyalty points expiring, seasonal push - one nudge can pull them back.

## What the K-Means check says

K-Means clustering on standardised Recency/Frequency/Monetary settled on k=5 (silhouette 0.671), which independently rediscovers the same business archetypes the rule-based segments describe: 
- Cluster 0: 296 customers, last order ~18 days ago, ~6.3 orders/year, INR 0.1L yearly spend.

- Cluster 1: 630 customers, last order ~296 days ago, ~2.1 orders/year, INR 0.0L yearly spend.

- Cluster 2: 241 customers, last order ~32 days ago, ~22.7 orders/year, INR 0.6L yearly spend.

- Cluster 3: 81 customers, last order ~10 days ago, ~47.8 orders/year, INR 1.9L yearly spend.

- Cluster 4: 252 customers, last order ~171 days ago, ~17.8 orders/year, INR 0.5L yearly spend.

Two different methods agreeing is a good sign the segments are real structure in the data, not artefacts of the cut-off rules.

## Limitations (read before acting on this)

- The data is synthetic: patterns are designed to look realistic, but real customer behaviour is messier.

- RFM scores are relative quintiles - a '5' means top-20% of *this* store, not an absolute loyalty standard.

- Segment rules are hand-written heuristics, not learned; boundary customers could flip segments with small rule tweaks.

- K-Means assumes roughly spherical clusters and equal variance; check the scatter chart for overlap before trusting cluster labels.

- Recency uses one reference date; seasonal shoppers may look 'Lost' mid-cycle and return on their own.
