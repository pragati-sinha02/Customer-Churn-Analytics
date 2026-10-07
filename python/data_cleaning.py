"""
data_cleaning.py
-----------------
Cleans the raw Telco Customer Churn dataset and saves a cleaned CSV.

Run from the PROJECT ROOT:
    python python/data_cleaning.py

Input:  data/customer_churn.csv
Output: data/cleaned_customer_churn.csv

Verified against the actual dataset (7043 rows, 21 columns) on 2026-09-03.
If your downloaded copy has different column names, see the NOTE at the
bottom of this file for how to adapt it.
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# 1. Paths (relative to project root, so this works on any machine)
# ---------------------------------------------------------------------------
RAW_PATH = os.path.join("data", "customer_churn.csv")
CLEAN_PATH = os.path.join("data", "cleaned_customer_churn.csv")


def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find '{path}'. Make sure customer_churn.csv is inside "
            f"the 'data' folder and that you're running this script from the "
            f"project root (Customer-Churn-Analytics/)."
        )
    return pd.read_csv(path)


def inspect(df: pd.DataFrame) -> None:
    print("Shape:", df.shape)
    print("\nColumns:", list(df.columns))
    print("\nDtypes:\n", df.dtypes)
    print("\nMissing values:\n", df.isnull().sum())
    print("\nDuplicate rows:", df.duplicated().sum())


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- 1. TotalCharges is stored as text and has 11 blank strings ---------
    # (all belong to brand-new customers with tenure == 0). Convert to numeric;
    # blanks become NaN, then we fill them with 0 since no charges have
    # accrued yet for a customer with 0 months of tenure.
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0)

    # --- 2. Duplicates -------------------------------------------------------
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="customerID")

    # --- 3. Standardize categorical text (strip whitespace) -----------------
    categorical_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in categorical_cols:
        df[col] = df[col].astype(str).str.strip()

    # --- 4. Normalize "No internet service" / "No phone service" ------------
    # These are functionally the same as "No" for churn analysis and modeling
    # (they only exist because the customer doesn't have that base service).
    replace_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies",
    ]
    for col in replace_cols:
        df[col] = df[col].replace("No internet service", "No")
    df["MultipleLines"] = df["MultipleLines"].replace("No phone service", "No")

    # --- 5. SeniorCitizen is 0/1 int; keep it but also add a readable label --
    df["SeniorCitizen"] = df["SeniorCitizen"].astype(int)

    # --- 6. Sanity-check target column ---------------------------------------
    df["Churn"] = df["Churn"].str.strip()
    assert set(df["Churn"].unique()) <= {"Yes", "No"}, "Unexpected Churn values found."

    # --- 7. Reset index -------------------------------------------------------
    df = df.reset_index(drop=True)

    return df


def main():
    print("Loading raw data...")
    df_raw = load_data(RAW_PATH)

    print("\n--- BEFORE CLEANING ---")
    inspect(df_raw)

    df_clean = clean_data(df_raw)

    print("\n--- AFTER CLEANING ---")
    inspect(df_clean)

    os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
    df_clean.to_csv(CLEAN_PATH, index=False)
    print(f"\nSaved cleaned data to '{CLEAN_PATH}' ({df_clean.shape[0]} rows, {df_clean.shape[1]} cols).")


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------
# NOTE — if your dataset's column names differ:
# Run this once in a Python shell to see your actual columns, then edit the
# column names referenced above (TotalCharges, Churn, customerID, etc.) to match:
#
#   import pandas as pd
#   df = pd.read_csv("data/customer_churn.csv")
#   print(df.columns.tolist())
# ---------------------------------------------------------------------------