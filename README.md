# Day 6 — RFM Customer Segmentation

Segment 1,500 e-commerce customers using **RFM analysis** (Recency, Frequency,
Monetary), score each dimension into quintiles, assign rule-based business
segments, and cross-check the structure with **K-Means clustering**. A
template-driven narrative generator (`ai_insights.py`) turns the numbers into
plain-English findings and per-segment marketing actions — that plus the ML
clustering is the "AI integrated" part.

## What it does

1. `generate_data.py` — builds one year of synthetic transactions (fixed seed
   `42`, reproducible). No external APIs.
2. `rfm_segmentation.py` — the main pipeline:
   - aggregates orders into Recency / Frequency / Monetary per customer
   - scores each dimension 1–5 with quintiles (5 = best)
   - maps score triples to segments (Champions, Loyal Customers, At Risk, …)
   - runs K-Means on standardised RFM for k = 2…8, picks k by silhouette score
   - saves 4 charts to `charts/` and a machine-readable `findings.json`
   - calls `ai_insights.py` to write `AI_INSIGHTS.md`
3. `ai_insights.py` — generates the plain-English insight narrative from
   `findings.json`.

## Key findings

- **1,500 customers, 17,021 orders, INR 494.7 lakh revenue** in the last year.
- **Champions (343 customers, 23%) drive 62% of revenue** — retention here is
  the highest-ROI activity. Median customer: last order 174 days ago,
  5 orders/year, INR 9,605/year.
- **Loyal Customers (447, 30%) add another 32% of revenue** — the top two
  segments are 53% of customers but 94% of revenue (classic Pareto shape).
- **~600 customers (40%) are At Risk / Hibernating / Lost**, holding only ~4%
  of revenue — win-back campaigns, not paid acquisition, are the right spend.
- **K-Means independently settled on k = 5 (silhouette 0.671)** and
  rediscovers the same archetypes: a whale cluster (81 customers,
  INR 1.85L avg yearly spend), steady actives, and a large dormant group —
  good evidence the segments are real structure, not rule artefacts.

Full narrative with a per-segment action plan: see `AI_INSIGHTS.md`.

## How to run

```bash
pip install -r requirements.txt
python3 rfm_segmentation.py
```

Outputs: `charts/*.png`, `findings.json`, `AI_INSIGHTS.md`.
The transaction CSV is large (~750 KB), so it is **not** committed — run
`python3 generate_data.py` to regenerate `data/transactions.csv` and
`data/customers.csv` yourself (seeded, so you get identical data).

## Files

| File | Purpose |
|---|---|
| `generate_data.py` | Synthetic data generator (seed 42) |
| `rfm_segmentation.py` | Main analysis pipeline |
| `ai_insights.py` | Plain-English narrative generator |
| `AI_INSIGHTS.md` | Auto-generated findings + actions |
| `findings.json` | Machine-readable results |
| `INTERVIEW_NOTES.md` | Interview Q&A prep for this project |
| `charts/` | 4 analysis charts |
| `data/customers.csv` | Customer master (transactions regenerated, not committed) |
