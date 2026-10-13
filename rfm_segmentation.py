"""RFM Customer Segmentation - main analysis script.

Pipeline (runs end to end):
    1. Generate (or reuse) synthetic transaction data        -> generate_data.py
    2. Compute Recency / Frequency / Monetary per customer
    3. Score each dimension 1-5 with quintiles -> rule-based segments
    4. K-Means clustering on scaled RFM (k chosen by silhouette score)
    5. Save charts                                          -> charts/*.png
    6. Save machine-readable summary                        -> findings.json
    7. Generate the plain-English AI narrative              -> ai_insights.py

Usage:  python3 rfm_segmentation.py
"""
import json
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless: save figures, don't open windows
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import generate_data
import ai_insights

REFERENCE_DATE = pd.Timestamp(generate_data.END_DATE)
CHART_DIR = "charts"


def rfm_segment(r, f, m):
    """Map an (R, F, M) score triple (each 1-5) to a business segment."""
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"
    if r >= 4 and f <= 2:
        return "New Customers" if f == 1 else "Potential Loyalists"
    if r <= 2 and f >= 4 and m >= 4:
        return "Can't Lose Them"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f <= 2:
        return "Hibernating" if m >= 3 else "Lost"
    if r == 3 and f <= 2:
        return "About to Sleep"
    return "Needs Attention"


def compute_rfm(transactions):
    """Aggregate raw orders into one Recency/Frequency/Monetary row per customer."""
    tx = transactions.copy()
    tx["order_date"] = pd.to_datetime(tx["order_date"])
    rfm = tx.groupby("customer_id").agg(
        last_order=("order_date", "max"),
        Frequency=("order_id", "count"),
        Monetary=("amount_inr", "sum"),
    )
    rfm["Recency"] = (REFERENCE_DATE - rfm["last_order"]).dt.days
    rfm.drop(columns="last_order", inplace=True)
    return rfm


def score_rfm(rfm):
    """Quintile scores 1-5 on each dimension (5 = best, i.e. most recent)."""
    scored = rfm.copy()
    scored["R"] = pd.qcut(scored["Recency"].rank(method="first"), 5,
                          labels=[5, 4, 3, 2, 1]).astype(int)
    scored["F"] = pd.qcut(scored["Frequency"].rank(method="first"), 5,
                          labels=[1, 2, 3, 4, 5]).astype(int)
    scored["M"] = pd.qcut(scored["Monetary"].rank(method="first"), 5,
                          labels=[1, 2, 3, 4, 5]).astype(int)
    scored["segment"] = [rfm_segment(r, f, m)
                         for r, f, m in zip(scored["R"], scored["F"], scored["M"])]
    return scored


def cluster_rfm(rfm, k_min=2, k_max=8, seed=42):
    """K-Means on standardised RFM; pick k with the best silhouette score."""
    X = StandardScaler().fit_transform(rfm[["Recency", "Frequency", "Monetary"]])
    results = {}
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=seed)
        labels = km.fit_predict(X)
        results[k] = {
            "inertia": float(km.inertia_),
            "silhouette": float(silhouette_score(X, labels)),
            "labels": labels,
            "model": km,
        }
    best_k = max(results, key=lambda k: results[k]["silhouette"])
    return best_k, results


def describe_cluster(rfm, labels, cluster_id):
    """Plain-English profile of one K-Means cluster."""
    c = rfm[labels == cluster_id]
    return {
        "size": int((labels == cluster_id).sum()),
        "avg_recency_days": round(float(c["Recency"].mean()), 1),
        "avg_orders": round(float(c["Frequency"].mean()), 1),
        "avg_spend_inr": round(float(c["Monetary"].mean()), 0),
    }


def save_charts(rfm, seg_summary, best_k, k_results):
    """Save the four analysis charts as PNG files."""
    os.makedirs(CHART_DIR, exist_ok=True)
    blue, teal, coral = "#2563eb", "#0d9488", "#f43f5e"

    # 1. RFM distributions
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, col, title in zip(axes,
                              ["Recency", "Frequency", "Monetary"],
                              ["Recency (days since last order)",
                               "Frequency (orders per year)",
                               "Monetary (INR per year)"]):
        ax.hist(rfm[col], bins=30, color=blue, edgecolor="white")
        ax.set_title(title, fontsize=10)
        ax.set_ylabel("customers")
    fig.suptitle("RFM distributions - heavily skewed, as in real retail data",
                 fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/rfm_distributions.png", dpi=150)
    plt.close(fig)

    # 2. Segments: customer share vs revenue share
    seg = seg_summary.sort_values("revenue_inr", ascending=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].barh(seg["segment"], seg["customers"], color=teal)
    axes[0].set_title("Customers per segment")
    axes[1].barh(seg["segment"], seg["revenue_inr"] / 1e5, color=coral)
    axes[1].set_title("Revenue per segment (INR lakh)")
    fig.suptitle("Rule-based RFM segments", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/segment_overview.png", dpi=150)
    plt.close(fig)

    # 3. K-Means clusters in Recency x Monetary space
    labels = k_results[best_k]["labels"]
    fig, ax = plt.subplots(figsize=(7.5, 5))
    sc = ax.scatter(rfm["Recency"], rfm["Monetary"] / 1000, c=labels,
                    cmap="tab10", alpha=0.55, s=18)
    ax.set_xlabel("Recency (days)")
    ax.set_ylabel("Monetary (INR thousand)")
    ax.set_title(f"K-Means clusters in RFM space (k={best_k})",
                 fontsize=11, fontweight="bold")
    fig.colorbar(sc, ax=ax, label="cluster")
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/kmeans_clusters.png", dpi=150)
    plt.close(fig)

    # 4. Elbow + silhouette for k selection
    ks = sorted(k_results)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    axes[0].plot(ks, [k_results[k]["inertia"] for k in ks], "o-", color=blue)
    axes[0].set_title("Elbow curve (inertia vs k)")
    axes[0].set_xlabel("k"); axes[0].set_ylabel("inertia")
    axes[1].plot(ks, [k_results[k]["silhouette"] for k in ks], "o-", color=teal)
    axes[1].axvline(best_k, color=coral, linestyle="--", label=f"best k={best_k}")
    axes[1].set_title("Silhouette score vs k")
    axes[1].set_xlabel("k"); axes[1].set_ylabel("silhouette"); axes[1].legend()
    fig.suptitle("Choosing the number of clusters", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(f"{CHART_DIR}/k_selection.png", dpi=150)
    plt.close(fig)
    print(f"Charts saved to {CHART_DIR}/")


def main():
    if not (os.path.exists("data/transactions.csv")
            and os.path.exists("data/customers.csv")):
        print("No data found - generating synthetic data...")
        generate_data.main()

    transactions = pd.read_csv("data/transactions.csv")
    rfm = compute_rfm(transactions)
    scored = score_rfm(rfm)

    # Segment summary table
    seg_summary = (scored.groupby("segment")
                   .agg(customers=("Monetary", "size"),
                        revenue_inr=("Monetary", "sum"),
                        avg_recency_days=("Recency", "mean"),
                        avg_orders=("Frequency", "mean"))
                   .reset_index())
    total_rev = float(scored["Monetary"].sum())
    seg_summary["revenue_share"] = seg_summary["revenue_inr"] / total_rev

    # K-Means
    best_k, k_results = cluster_rfm(rfm)
    labels = k_results[best_k]["labels"]
    scored["kmeans_cluster"] = labels
    clusters = {str(cid): describe_cluster(rfm, labels, cid)
                for cid in range(best_k)}

    save_charts(rfm, seg_summary, best_k, k_results)

    findings = {
        "reference_date": str(generate_data.END_DATE),
        "n_customers": int(len(scored)),
        "n_transactions": int(len(transactions)),
        "total_revenue_inr": round(total_rev, 0),
        "rfm_medians": {c: round(float(rfm[c].median()), 1)
                        for c in ["Recency", "Frequency", "Monetary"]},
        "segments": seg_summary.sort_values("revenue_inr", ascending=False)
                               .round(2).to_dict(orient="records"),
        "kmeans": {
            "best_k": best_k,
            "silhouette": round(k_results[best_k]["silhouette"], 3),
            "all_silhouettes": {str(k): round(k_results[k]["silhouette"], 3)
                                for k in sorted(k_results)},
            "clusters": clusters,
        },
    }
    with open("findings.json", "w", encoding="utf-8") as fh:
        json.dump(findings, fh, indent=2)
    print(f"findings.json written ({len(scored)} customers, "
          f"k={best_k}, silhouette={findings['kmeans']['silhouette']})")

    ai_insights.main()   # build the plain-English narrative


if __name__ == "__main__":
    main()
