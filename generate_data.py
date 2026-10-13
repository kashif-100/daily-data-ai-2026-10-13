"""Generate synthetic e-commerce transaction data for the RFM segmentation project.

The data is fully synthetic (fixed random seed -> reproducible) and is built
from six hidden customer archetypes so the RFM segments have a realistic shape.
No external APIs are used.

Outputs:
    data/transactions.csv  - one row per purchase
    data/customers.csv     - one row per customer (signup date, city, channel)
"""
import os
import numpy as np
import pandas as pd
from datetime import date, timedelta

SEED = 42
N_CUSTOMERS = 1500
END_DATE = date(2026, 10, 13)          # "today" for the analysis
HISTORY_DAYS = 365                     # one full year of history

CATEGORIES = ["Electronics", "Apparel", "Groceries", "Home & Kitchen", "Beauty"]
CATEGORY_W = [0.25, 0.25, 0.20, 0.15, 0.15]
CHANNELS = ["App", "Website", "Store"]
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Pune", "Hyderabad", "Chennai",
          "Kolkata", "Ahmedabad", "Jaipur", "Nagpur"]

# name, share of customers, orders-per-year range, days-since-last-order range,
# average order value (INR)
ARCHETYPES = [
    ("champions",   0.08, (25, 60), (0, 20),    3200),
    ("loyal",       0.15, (12, 28), (10, 60),   2200),
    ("potential",   0.18, (3, 7),   (0, 30),    1400),
    ("at_risk",     0.17, (10, 25), (120, 220), 2400),
    ("hibernating", 0.15, (2, 5),   (200, 340), 1800),
    ("lost",        0.27, (1, 2),    (250, 360), 900),
]


def build_customers(rng):
    """Create the customer table (archetype column is dropped before saving)."""
    shares = np.array([a[1] for a in ARCHETYPES])
    archetype_idx = rng.choice(len(ARCHETYPES), size=N_CUSTOMERS, p=shares)
    customers = pd.DataFrame({
        "customer_id": [f"C{100000 + i}" for i in range(N_CUSTOMERS)],
        "signup_date": [
            END_DATE - timedelta(days=int(rng.integers(30, 900)))
            for _ in range(N_CUSTOMERS)
        ],
        "city": rng.choice(CITIES, size=N_CUSTOMERS),
        "acquisition_channel": rng.choice(CHANNELS, size=N_CUSTOMERS),
        "_archetype": archetype_idx,   # hidden ground truth, not saved
    })
    return customers


def build_transactions(customers, rng):
    """Create one transaction row per purchase."""
    rows = []
    order_id = 1
    for _, cust in customers.iterrows():
        _, _, freq_rng, rec_rng, aov = ARCHETYPES[int(cust["_archetype"])]
        n_orders = int(rng.integers(freq_rng[0], freq_rng[1] + 1))
        days_since_last = int(rng.integers(rec_rng[0], rec_rng[1] + 1))
        last_date = END_DATE - timedelta(days=days_since_last)

        # Spread the earlier orders randomly across the year before last purchase
        earliest = END_DATE - timedelta(days=HISTORY_DAYS)
        if n_orders == 1:
            order_dates = [last_date]
        else:
            others = sorted(rng.choice(
                pd.date_range(earliest, last_date - timedelta(days=1)).date,
                size=n_orders - 1, replace=True))
            order_dates = others + [last_date]

        for od in order_dates:
            amount = round(float(rng.lognormal(mean=np.log(aov), sigma=0.6)), 2)
            rows.append({
                "order_id": f"O{200000 + order_id}",
                "customer_id": cust["customer_id"],
                "order_date": od.isoformat(),
                "category": rng.choice(CATEGORIES, p=CATEGORY_W),
                "amount_inr": amount,
            })
            order_id += 1
    return pd.DataFrame(rows)


def main():
    rng = np.random.default_rng(SEED)
    os.makedirs("data", exist_ok=True)

    customers = build_customers(rng)
    transactions = build_transactions(customers, rng)

    # The archetype column is only design scaffolding - drop it so the
    # analysis works from raw transaction data like a real analyst would.
    customers.drop(columns=["_archetype"]).to_csv("data/customers.csv", index=False)
    transactions.to_csv("data/transactions.csv", index=False)

    print(f"Customers   : {len(customers)}")
    print(f"Transactions: {len(transactions)}")
    print(f"Total revenue: INR {transactions['amount_inr'].sum():,.0f}")
    print("Saved to data/")


if __name__ == "__main__":
    main()
