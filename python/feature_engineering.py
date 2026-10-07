"""
feature_engineering.py
------------------------
Adds a small set of business-meaningful features on top of the cleaned data.
Kept deliberately minimal — every feature has a clear analytical reason.

Run from the PROJECT ROOT (after data_cleaning.py):
    python python/feature_engineering.py

Input:  data/cleaned_customer_churn.csv
Output: data/cleaned_customer_churn.csv  (overwritten with new columns added)
"""

import os
import pandas as pd

CLEAN_PATH = os.path.join("data", "cleaned_customer_churn.csv")


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. TenureGroup — bins tenure (months) into buckets that map to
    #    the "0-12 / 12-24 / 24-48 / 48+" segments commonly used in telco
    #    retention reporting. Raw tenure is noisy for grouped BI charts.
    bins = [-1, 12, 24, 48, 60, df["tenure"].max()]
    labels = ["0-12", "13-24", "25-48", "49-60", "60+"]
    df["TenureGroup"] = pd.cut(df["tenure"], bins=bins, labels=labels)

    # 2. AvgMonthlySpend — TotalCharges / tenure gives a smoothed monthly
    #    spend figure that is more stable than MonthlyCharges alone for
    #    customers whose plan changed over time. Guard against tenure == 0.
    df["AvgMonthlySpend"] = df.apply(
        lambda r: r["TotalCharges"] / r["tenure"] if r["tenure"] > 0 else r["MonthlyCharges"],
        axis=1,
    )

    # 3. NumAddOnServices — counts how many of the 6 optional services
    #    (OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport,
    #    StreamingTV, StreamingMovies) the customer has activated. More
    #    add-ons is a known "stickiness" signal in churn analysis.
    addon_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies",
    ]
    df["NumAddOnServices"] = (df[addon_cols] == "Yes").sum(axis=1)

    # 4. IsNewCustomer — flags customers with tenure <= 6 months, who
    #    consistently show the highest churn risk in telco datasets and
    #    are useful as a standalone slicer in Power BI.
    df["IsNewCustomer"] = (df["tenure"] <= 6).astype(int)

    # 5. HasMultipleServices — flags customers who have BOTH phone and
    #    internet service, a common upsell/bundling indicator.
    df["HasMultipleServices"] = (
        (df["PhoneService"] == "Yes") & (df["InternetService"] != "No")
    ).astype(int)

    return df


def main():
    if not os.path.exists(CLEAN_PATH):
        raise FileNotFoundError(
            f"'{CLEAN_PATH}' not found. Run 'python python/data_cleaning.py' first."
        )

    df = pd.read_csv(CLEAN_PATH)
    df_feat = add_features(df)

    print("New columns added:", [c for c in df_feat.columns if c not in df.columns])
    print("\nShape after feature engineering:", df_feat.shape)
    print("\nTenureGroup distribution:\n", df_feat["TenureGroup"].value_counts())
    print("\nNumAddOnServices distribution:\n", df_feat["NumAddOnServices"].value_counts().sort_index())

    df_feat.to_csv(CLEAN_PATH, index=False)
    print(f"\nSaved enriched dataset back to '{CLEAN_PATH}'.")


if __name__ == "__main__":
    main()