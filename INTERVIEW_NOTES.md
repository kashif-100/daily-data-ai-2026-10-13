# INTERVIEW NOTES — Day 6: RFM Customer Segmentation

## 30-second pitch

"I segmented 1,500 e-commerce customers with RFM analysis — scoring everyone
1 to 5 on recency, frequency and monetary value, then mapping those scores to
business segments like Champions and At Risk. I cross-checked the segments with
K-Means clustering, which independently found 5 clusters with a silhouette
score of 0.67, and I built a narrative generator that turns the numbers into a
per-segment marketing action plan. The headline: 23% of customers drive 62% of
revenue, so retention beats acquisition."

## Project walkthrough

- **Data:** fully synthetic — 1 year of transactions for 1,500 customers,
  generated with a fixed seed (42) from six hidden archetypes (champions,
  loyal, at-risk, hibernating, …). Synthetic data keeps the project
  reproducible and honest: patterns look realistic but nobody's real purchase
  history is involved, and every number regenerates identically.
- **Step 1:** aggregate raw orders into one row per customer — Recency (days
  since last order, reference date 2026-10-13), Frequency (order count),
  Monetary (total INR spend).
- **Step 2:** convert each dimension to a 1–5 quintile score (`pd.qcut` on
  ranked values so every bin is equally populated; 5 = best, i.e. most recent
  for Recency).
- **Step 3:** hand-written rules map (R, F, M) triples to segments — e.g.
  (5,5,5)-ish → Champions, low recency + high frequency → Can't Lose Them.
- **Step 4:** K-Means on standardised RFM for k = 2…8, pick k by silhouette
  score (k = 5, silhouette 0.671).
- **Step 5:** save 4 charts, `findings.json`, and run `ai_insights.py`, which
  renders the narrative in `AI_INSIGHTS.md` — one profile + marketing action
  per segment.

## Technical deep-dives

**Why quintiles instead of fixed cut-offs?** Absolute thresholds ("spent over
INR 50,000") don't transfer between businesses; quintiles adapt to the data
distribution automatically. Limitation: a score of 5 means "top 20% of *this*
store", not an absolute loyalty standard, so scores aren't comparable across
datasets.

**Why `rank(method='first')` before `qcut`?** Real RFM columns are full of
ties (hundreds of customers with Frequency = 1). `qcut` on raw values can
collapse bins when edges duplicate; ranking with `method='first'` breaks ties
arbitrarily but guarantees five equal bins.

**K-Means on scaled data — why scale?** K-Means minimises Euclidean distance,
so the raw Monetary column (thousands of rupees) would completely dominate
Recency (days) and Frequency (counts). `StandardScaler` puts all three on
unit variance so each dimension votes equally. Limitation: K-Means assumes
roughly spherical, equal-variance clusters — fine here (silhouette 0.67) but
worth checking the scatter chart for overlap before trusting labels.

**Choosing k with the silhouette score:** silhouette measures how much closer
each point is to its own cluster than to the nearest other cluster (range
-1…1). We tried k = 2…8; k = 5 scored 0.671, the peak, and the elbow curve
agrees. The elbow alone is subjective — silhouette gives a number to defend.

**Why both rule-based segments AND K-Means?** The rules give business-friendly
labels a marketer can act on; K-Means is unsupervised, so when it rediscovers
the same archetypes (whales, actives, dormants) it's independent validation
that the structure is real, not an artefact of my hand-written cut-offs.

## Data-analyst thinking

- **KPIs:** revenue share per segment, customer share per segment, average
  recency per segment, segment migration risk (At Risk → Lost).
- **Key insight:** Pareto shape — Champions (23% of customers) produce 62% of
  revenue, and the top two segments produce 94%. Meanwhile ~40% of customers
  are cooling or gone but hold only ~4% of revenue.
- **From analysis to recommendations:** because value is concentrated,
  retention of Champions/Loyal (loyalty perks, early access) has far higher
  expected ROI than broad acquisition; the At Risk / Can't Lose Them groups
  get time-limited win-back offers on categories they already bought; Lost
  customers are suppressed from paid media (cheap newsletter only) because
  reactivation cost exceeds expected value.

## The "AI integrated" part

"AI integrated" here means two things. First, the ML: K-Means clustering
discovers customer groups from the data without labels, and the silhouette
score automates the k-selection decision. Second, the narrative generator:
`ai_insights.py` reads `findings.json` and writes a plain-English report —
executive summary, one profile + marketing action per segment, and stated
limitations. Trade-off vs alternatives: it's template-driven, not an LLM, so
it's deterministic, free, and never hallucinates numbers — but it can't reason
about anything not encoded in the templates. For a portfolio project that's
the right trade: every sentence in AI_INSIGHTS.md is traceable to a number in
findings.json.

## With more time I would…

- Add segment migration analysis (how many customers moved At Risk → Lost
  quarter over quarter) to make the win-back urgency concrete.
- Try DBSCAN or Gaussian mixtures to see if non-spherical clusters fit better,
  and compare with the K-Means result.
- Build a simple propensity model (logistic regression on RFM features)
  predicting "will churn in the next 90 days" and evaluate it with
  precision/recall.
- Validate on real data — e.g. the UCI Online Retail dataset — to show the
  pipeline works beyond synthetic data.
- Turn the action plan into a simulated campaign ROI estimate: expected
  response rate × margin per segment vs. campaign cost.
