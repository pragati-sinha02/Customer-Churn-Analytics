"""
churn_model.py
---------------
End-to-end churn prediction pipeline: Logistic Regression vs Random Forest.

Run from the PROJECT ROOT (after data_cleaning.py and feature_engineering.py):
    python python/churn_model.py

Input:  data/cleaned_customer_churn.csv
Output: data/churn_predictions.csv
        outputs/figures/confusion_matrix_logreg.png
        outputs/figures/confusion_matrix_rf.png
        outputs/figures/roc_curve.png
        outputs/figures/feature_importance_rf.png
        outputs/figures/churn_probability_distribution.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # safe for headless / script execution
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, ConfusionMatrixDisplay,
)

DATA_PATH = os.path.join("data", "cleaned_customer_churn.csv")
PRED_PATH = os.path.join("data", "churn_predictions.csv")
FIG_DIR = os.path.join("outputs", "figures")
RANDOM_STATE = 42


def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"'{DATA_PATH}' not found. Run data_cleaning.py and "
            f"feature_engineering.py first."
        )
    return pd.read_csv(DATA_PATH)


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    # customerID is an identifier, not a predictive feature -> excluded upstream.
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object", "string"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ]
    )
    return preprocessor, numeric_cols, categorical_cols


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(PRED_PATH), exist_ok=True)

    df = load_data()

    # --- Target ---------------------------------------------------------
    y = (df["Churn"] == "Yes").astype(int)

    # --- Features ---------------------------------------------------------
    # Drop identifier + target + TenureGroup (a binned duplicate of `tenure`,
    # kept only for BI/reporting, not needed by the model -> avoids redundancy).
    drop_cols = ["customerID", "Churn", "TenureGroup"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])

    preprocessor, num_cols, cat_cols = build_preprocessor(X)
    print(f"Numeric features ({len(num_cols)}):", num_cols)
    print(f"Categorical features ({len(cat_cols)}):", cat_cols)

    # --- Train/test split (stratified because churn classes are imbalanced,
    #     ~26.5% positive) ---------------------------------------------------
    X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
        X, y, df["customerID"],
        test_size=0.2, random_state=RANDOM_STATE, stratify=y,
    )
    print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")
    print(f"Churn rate — train: {y_train.mean():.3f}, test: {y_test.mean():.3f}")

    # --- Model 1: Logistic Regression --------------------------------------
    logreg_pipe = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
    ])
    logreg_pipe.fit(X_train, y_train)
    logreg_probs = logreg_pipe.predict_proba(X_test)[:, 1]
    logreg_preds = logreg_pipe.predict(X_test)

    # --- Model 2: Random Forest ---------------------------------------------
    rf_pipe = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", RandomForestClassifier(
            n_estimators=300, max_depth=10, random_state=RANDOM_STATE, n_jobs=-1
        )),
    ])
    rf_pipe.fit(X_train, y_train)
    rf_probs = rf_pipe.predict_proba(X_test)[:, 1]
    rf_preds = rf_pipe.predict(X_test)

    # --- Evaluate both models -------------------------------------------------
    def evaluate(name, y_true, preds, probs):
        return {
            "Model": name,
            "Accuracy": accuracy_score(y_true, preds),
            "Precision": precision_score(y_true, preds),
            "Recall": recall_score(y_true, preds),
            "F1": f1_score(y_true, preds),
            "ROC-AUC": roc_auc_score(y_true, probs),
        }

    results = [
        evaluate("Logistic Regression", y_test, logreg_preds, logreg_probs),
        evaluate("Random Forest", y_test, rf_preds, rf_probs),
    ]
    results_df = pd.DataFrame(results)
    print("\n=== MODEL COMPARISON ===")
    print(results_df.to_string(index=False))

    # --- Select the better model based on ROC-AUC (robust to class
    #     imbalance and threshold choice, unlike raw accuracy) -----------------
    best_idx = results_df["ROC-AUC"].idxmax()
    best_name = results_df.loc[best_idx, "Model"]
    print(f"\nSelected model (highest ROC-AUC): {best_name}")

    if best_name == "Random Forest":
        best_pipe, best_probs, best_preds = rf_pipe, rf_probs, rf_preds
    else:
        best_pipe, best_probs, best_preds = logreg_pipe, logreg_probs, logreg_preds

    # --- Confusion matrices for BOTH models (for the report/README) ----------
    for name, preds in [("logreg", logreg_preds), ("rf", rf_preds)]:
        cm = confusion_matrix(y_test, preds)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No Churn", "Churn"])
        fig, ax = plt.subplots(figsize=(5, 4))
        disp.plot(ax=ax, cmap="Blues", colorbar=False)
        ax.set_title(f"Confusion Matrix — {'Logistic Regression' if name=='logreg' else 'Random Forest'}")
        fig.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, f"confusion_matrix_{name}.png"), dpi=150)
        plt.close(fig)

    # --- ROC curve (both models on one plot) ----------------------------------
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, probs in [("Logistic Regression", logreg_probs), ("Random Forest", rf_probs)]:
        fpr, tpr, _ = roc_curve(y_test, probs)
        auc = roc_auc_score(y_test, probs)
        ax.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random guess")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve — Churn Prediction Models")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "roc_curve.png"), dpi=150)
    plt.close(fig)

    # --- Feature importance (Random Forest only — logistic coefficients
    #     aren't directly comparable across one-hot categories) ----------------
    if best_name == "Random Forest" or True:  # always produce it for the report
        ohe = rf_pipe.named_steps["preprocessor"].named_transformers_["cat"]
        cat_feature_names = ohe.get_feature_names_out(cat_cols)
        all_feature_names = np.concatenate([num_cols, cat_feature_names])
        importances = rf_pipe.named_steps["model"].feature_importances_
        importance_df = pd.DataFrame({
            "feature": all_feature_names, "importance": importances
        }).sort_values("importance", ascending=False).head(15)

        fig, ax = plt.subplots(figsize=(7, 6))
        ax.barh(importance_df["feature"][::-1], importance_df["importance"][::-1], color="#4C72B0")
        ax.set_title("Top 15 Feature Importances — Random Forest")
        ax.set_xlabel("Importance")
        fig.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, "feature_importance_rf.png"), dpi=150)
        plt.close(fig)

    # --- Churn probability distribution (best model) ---------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(best_probs[y_test == 0], bins=30, alpha=0.6, label="Actual: No Churn")
    ax.hist(best_probs[y_test == 1], bins=30, alpha=0.6, label="Actual: Churn")
    ax.set_xlabel("Predicted Churn Probability")
    ax.set_ylabel("Number of Customers")
    ax.set_title(f"Churn Probability Distribution — {best_name}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "churn_probability_distribution.png"), dpi=150)
    plt.close(fig)

    # --- Generate predictions.csv for the FULL customer base (not just test
    #     set) so Power BI has a row per customer, using the trained best model ---
    full_probs = best_pipe.predict_proba(X)[:, 1]
    full_preds = best_pipe.predict(X)

    # Risk thresholds: chosen using the natural tercile-like split observed in
    # the probability distribution — customers below 0.3 are unlikely to churn,
    # 0.3-0.6 is a genuine toss-up zone worth proactive outreach, above 0.6 is
    # high-confidence risk. Documented explicitly so it's not a "magic number".
    def risk_bucket(p):
        if p < 0.30:
            return "Low Risk"
        elif p < 0.60:
            return "Medium Risk"
        else:
            return "High Risk"

    predictions_df = pd.DataFrame({
        "customerID": df["customerID"],
        "Contract": df["Contract"],
        "tenure": df["tenure"],
        "MonthlyCharges": df["MonthlyCharges"],
        "TotalCharges": df["TotalCharges"],
        "ActualChurn": df["Churn"],
        "ChurnProbability": full_probs.round(4),
        "PredictedChurn": np.where(full_preds == 1, "Yes", "No"),
        "RiskCategory": [risk_bucket(p) for p in full_probs],
    })
    predictions_df.to_csv(PRED_PATH, index=False)
    print(f"\nSaved predictions for {len(predictions_df)} customers to '{PRED_PATH}'.")
    print("\nRisk category distribution:")
    print(predictions_df["RiskCategory"].value_counts())

    # Save the metrics table too, for the README / business insights section.
    results_df.to_csv(os.path.join("outputs", "model_comparison_metrics.csv"), index=False)
    print(f"\nSaved model comparison metrics to 'outputs/model_comparison_metrics.csv'.")


if __name__ == "__main__":
    main()