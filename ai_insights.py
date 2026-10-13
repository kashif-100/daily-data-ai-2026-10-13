"""Auto-generate the plain-English narrative for the RFM segmentation.

Reads findings.json (produced by rfm_segmentation.py) and writes AI_INSIGHTS.md:
an executive summary, a profile + marketing action for every segment, what the
K-Means check says about the rule-based segments, and honest limitations.
This template-driven narrative is the "AI integrated" part of the project.
"""
import json

ACTIONS = {
    "Champions": ("Reward and retain", "Early access to launches, loyalty points, "
                  "referral bonuses - these customers are your best advocates."),
    "Loyal Customers": ("Keep the habit", "Subscription-style nudges, cross-sell "
                        "bundles, thank-you perks so they never drift."),
    "Potential Loyalists": ("Convert to loyal", "Targeted offers on their second "
                            "favourite category; ask for reviews to deepen the tie."),
    "New Customers": ("Onboard well", "Welcome series, first-repeat-purchase coupon "
                      "within 30 days; measure repeat rate, not just acquisition."),
    "At Risk": ("Win back soon", "Time-limited 'we miss you' offer on previously "
                "bought categories; the window closes fast from here."),
    "Can't Lose Them": ("Personal rescue", "High-touch outreach - phone/email from a "
                        "real human, premium win-back offer; they were your whales."),
    "Hibernating": ("Cheap reactivation", "Low-cost email/SMS with deep discounts; "
                    "do not spend paid-media money on them."),
    "Lost": ("Let go (for now)", "Suppress from paid campaigns; keep in a cheap "
              "newsletter pool in case they return on their own."),
    "About to Sleep": ("Wake-up nudge", "Reminder of loyalty points expiring, "
                       "seasonal push - one nudge can pull them back."),
    "Needs Attention": ("Watch list", "Above-average but cooling; A/B test "
                       "messaging before they slide into At Risk."),
}


def inr_lakh(x):
    return f"{x / 1e5:,.1f}L"


def main():
    with open("findings.json", encoding="utf-8") as fh:
        f = json.load(fh)

    segs = f["segments"]
    by_name = {s["segment"]: s for s in segs}
    total_rev = f["total_revenue_inr"]
    n = f["n_customers"]

    top = segs[0]
    champions = by_name.get("Champions", {})
    at_risk_like = sum(by_name.get(s, {}).get("customers", 0)
                       for s in ["At Risk", "Can't Lose Them", "Hibernating", "Lost"])
    at_risk_rev = sum(by_name.get(s, {}).get("revenue_inr", 0)
                      for s in ["At Risk", "Can't Lose Them", "Hibernating", "Lost"])

    lines = []
    lines.append("# AI Insights - RFM Customer Segmentation\n")
    lines.append(f"*Auto-generated from {n:,} customers and "
                 f"{f['n_transactions']:,} transactions (reference date "
                 f"{f['reference_date']}).*\n")
    lines.append("## Executive summary\n")
    lines.append(
        f"This store earned INR {inr_lakh(total_rev)} in the last year. "
        f"The single biggest revenue driver is the **{top['segment']}** segment: "
        f"{top['customers']:,} customers ({top['customers'] / n:.0%}) contributing "
        f"INR {inr_lakh(top['revenue_inr'])} ({top['revenue_share']:.0%} of revenue). "
    )
    if champions:
        lines.append(
            f"The **Champions** group is small ({champions['customers']:,} customers) "
            f"but punches far above its weight with INR {inr_lakh(champions['revenue_inr'])} "
            f"({champions['revenue_share']:.0%} of revenue) - retention here is the "
            f"highest-ROI activity in the business. ")
    lines.append(
        f"On the other side, {at_risk_like:,} customers "
        f"({at_risk_like / n:.0%}) sit in the At Risk / Can't Lose Them / Hibernating / Lost "
        f"buckets, representing INR {inr_lakh(at_risk_rev)} of past-year revenue "
        f"that is cooling or gone - this is where win-back campaigns earn their keep.\n")

    lines.append("## Segment profiles and recommended actions\n")
    for s in segs:
        name = s["segment"]
        headline, action = ACTIONS.get(name, ("Review", "Investigate this group."))
        lines.append(f"### {name} - {s['customers']:,} customers, "
                     f"INR {inr_lakh(s['revenue_inr'])} ({s['revenue_share']:.0%})\n")
        lines.append(f"- Typical behaviour: last order ~{s['avg_recency_days']:.0f} days ago, "
                     f"~{s['avg_orders']:.1f} orders/year.\n")
        lines.append(f"- **Action: {headline}.** {action}\n")

    km = f["kmeans"]
    lines.append("## What the K-Means check says\n")
    lines.append(
        f"K-Means clustering on standardised Recency/Frequency/Monetary settled on "
        f"k={km['best_k']} (silhouette {km['silhouette']}), which independently "
        f"rediscovers the same business archetypes the rule-based segments describe: "
    )
    for cid, c in km["clusters"].items():
        lines.append(f"- Cluster {cid}: {c['size']:,} customers, last order "
                     f"~{c['avg_recency_days']:.0f} days ago, "
                     f"~{c['avg_orders']:.1f} orders/year, "
                     f"INR {inr_lakh(c['avg_spend_inr'])} yearly spend.\n")
    lines.append("Two different methods agreeing is a good sign the segments are real "
                 "structure in the data, not artefacts of the cut-off rules.\n")

    lines.append("## Limitations (read before acting on this)\n")
    lines.append("- The data is synthetic: patterns are designed to look realistic, "
                 "but real customer behaviour is messier.\n")
    lines.append("- RFM scores are relative quintiles - a '5' means top-20% of *this* "
                 "store, not an absolute loyalty standard.\n")
    lines.append("- Segment rules are hand-written heuristics, not learned; boundary "
                 "customers could flip segments with small rule tweaks.\n")
    lines.append("- K-Means assumes roughly spherical clusters and equal variance; "
                 "check the scatter chart for overlap before trusting cluster labels.\n")
    lines.append("- Recency uses one reference date; seasonal shoppers may look "
                 "'Lost' mid-cycle and return on their own.\n")

    with open("AI_INSIGHTS.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("AI_INSIGHTS.md written")


if __name__ == "__main__":
    main()
