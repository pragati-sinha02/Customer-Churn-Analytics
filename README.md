# Customer Churn & Revenue Intelligence Analytics Platform

An end-to-end analytics project that identifies which customers are likely to
churn, quantifies the revenue at risk, and turns that into a Power BI
dashboard a business team could actually act on.

## Overview

Telecom companies lose a meaningful share of revenue every year to customer
churn. This project builds a complete pipeline — from raw data to a trained
ML model to an interactive dashboard — that flags at-risk customers before
they leave, so retention teams can prioritize outreach.

## Business Problem

Customer acquisition costs far more than retention. Without a systematic way
to score churn risk, retention efforts are reactive and unfocused. This
project answers three questions:
1. Which customer segments churn the most, and why?
2. How much monthly revenue is currently at risk?
3. Which *individual* customers should be prioritized for retention outreach?

## Objectives

- Clean and prepare the Telco Customer Churn dataset for analysis.
- Answer 20 business questions using SQL.
- Train and compare two churn-prediction models (Logistic Regression, Random Forest).
- Score every customer with a churn probability and risk category.
- Present findings in a 4-page Power BI dashboard for non-technical stakeholders.

## Dataset

**IBM Telco Customer Churn** dataset — 7,043 customers, 21 columns, sourced
from IBM's public sample dataset repository. Each row is one customer with
demographic info, account/contract details, subscribed services, billing
info, and whether they churned.

## Technologies

Python (Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn) · Jupyter Notebook ·
MySQL / MySQL Workbench · Power BI Desktop · Git & GitHub · VS Code

## Architecture

```
Raw CSV → Python cleaning → Feature engineering → [ MySQL (SQL analysis) ]
                                                  → [ Scikit-learn (ML model) ]
                                                            ↓
                                                  churn_predictions.csv
                                                            ↓
                                                     Power BI Dashboard
```

## Folder Structure

```
Customer-Churn-Analytics/
├── data/
│   ├── customer_churn.csv            # raw dataset
│   ├── cleaned_customer_churn.csv    # after cleaning + feature engineering
│   └── churn_predictions.csv         # model output, one row per customer
├── notebooks/
│   └── 01_EDA.ipynb                  # exploratory data analysis
├── python/
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   └── churn_model.py
├── sql/
│   ├── database.sql                  # schema + import instructions
│   └── analysis.sql                  # 20 business-question queries
├── powerbi/
│   └── churn_dashboard.pbix          # (you build this — see docs/02)
├── outputs/
│   ├── figures/                      # model evaluation charts
│   ├── predictions/
│   └── model_comparison_metrics.csv
├── docs/                             # setup, Power BI, GitHub, resume & interview guides
├── README.md
├── requirements.txt
└── .gitignore
```

## Data Cleaning

Handled in `python/data_cleaning.py`:
- `TotalCharges` was stored as text and had **11 blank values**, all belonging
  to customers with `tenure == 0` (brand-new customers with no billing history
  yet). Converted to numeric and filled with 0.
- Removed duplicate rows and duplicate `customerID`s (none were found in this
  dataset, but the check is in place for future data refreshes).
- Standardized `"No internet service"` / `"No phone service"` to `"No"` across
  6 add-on service columns, since they're functionally equivalent to "No" for
  churn analysis.
- Verified `Churn` only contains `{Yes, No}`.

## Exploratory Data Analysis

Full notebook: `notebooks/01_EDA.ipynb` (executed end-to-end, all cells run
without errors). Key findings from the actual output:

- **Overall churn rate: 26.54%** (1,869 of 7,043 customers).
- **Contract type is the strongest churn driver**: Month-to-month customers
  churn at **42.71%**, vs. 11.27% for one-year and just 2.83% for two-year
  contracts.
- **Fiber optic** internet customers churn at **41.89%**, more than double the
  DSL rate of 18.96%.
- **Electronic check** payers churn at **45.29%** — roughly 3x the rate of any
  automatic payment method (15–19%).
- Churned customers average **18.0 months** of tenure vs. **37.6 months** for
  retained customers — churn risk is heavily front-loaded early in the
  customer lifecycle.
- **Monthly revenue at risk** from already-churned customers: **~$139,131**
  (30.50% of total monthly recurring revenue of ~$456,117).

## SQL Analysis

`sql/analysis.sql` contains 20 commented business queries covering churn
rate, revenue at risk, segment-level churn (by contract, payment method,
internet service, tenure group, senior citizen status), high-value churned
customers, and a final management summary query. See `sql/database.sql` for
schema creation and CSV import steps via MySQL Workbench.

## Machine Learning

`python/churn_model.py` builds and compares two models inside a single
`ColumnTransformer` + `Pipeline` (no data leakage — all preprocessing is
fit only on the training split):

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.8048 | 0.6656 | 0.5321 | 0.5914 | **0.8458** |
| Random Forest | 0.7984 | 0.6510 | 0.5187 | 0.5774 | 0.8416 |

**Logistic Regression was selected** as the better model, based on ROC-AUC
(robust to the ~26.5% class imbalance, unlike raw accuracy). Full metrics are
saved to `outputs/model_comparison_metrics.csv`, and evaluation charts
(confusion matrices, ROC curve, feature importance, probability distribution)
are saved to `outputs/figures/`.

## Customer Risk Scoring

Every customer is scored with a churn probability and bucketed into:

| Risk Category | Probability Range | Customers |
|---|---|---|
| Low Risk | < 0.30 | 4,426 |
| Medium Risk | 0.30 – 0.60 | 1,613 |
| High Risk | ≥ 0.60 | 1,004 |

Thresholds were chosen from the natural shape of the predicted-probability
distribution (see `outputs/figures/churn_probability_distribution.png`), not
an arbitrary 50/50 cutoff — this keeps "Medium Risk" as a genuine toss-up
band worth proactive outreach, separate from high-confidence risk.

Output: `data/churn_predictions.csv` (customerID, contract, tenure, charges,
actual churn, churn probability, predicted churn, risk category).

## Power BI Dashboard

See `docs/02_mysql_and_powerbi_guide.md` for the complete step-by-step build
(data import, relationships, DAX measures, and all 4 dashboard pages):
Executive Overview, Customer Analysis, Churn Analysis, Customer Risk.

## Key Insights

> Insights below are drawn directly from this run's actual output (see EDA
> and ML sections above) — nothing here is invented.

- Month-to-month, fiber-optic, electronic-check customers form the highest-risk
  overlapping segment.
- New customers (tenure ≤ 6 months) are disproportionately likely to churn —
  the first six months are the critical retention window.
- The model separates churners from non-churners well (ROC-AUC 0.846) but has
  moderate recall (53.2%) — meaning roughly half of actual churners are
  missed at the default 0.5 threshold. Business teams using this model should
  rely on the probability score and risk bucket, not just the binary
  prediction, to decide who to contact.

## Business Recommendations

*(Recommendations — distinct from the findings above, which are strictly
observed facts from the data)*
- Offer incentives to convert month-to-month customers to annual contracts.
- Proactively reach out to customers in their first 6 months, especially on
  fiber-optic plans.
- Encourage a switch away from electronic check to automatic payment methods
  (e.g. a small discount), since payment friction correlates strongly with churn.
- Prioritize retention-team outreach using the "High Risk" list in
  `churn_predictions.csv` / Power BI Page 4, ordered by revenue at risk.

## How to Run

```bash
# 1. Set up environment (see docs/01_setup_guide.md for full detail)
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 2. Run the pipeline in order
python python/data_cleaning.py
python python/feature_engineering.py
python python/churn_model.py

# 3. Open notebooks/01_EDA.ipynb in VS Code and run all cells

# 4. Import cleaned_customer_churn.csv into MySQL (sql/database.sql)
#    and run sql/analysis.sql in MySQL Workbench

# 5. Open Power BI Desktop and follow docs/02_mysql_and_powerbi_guide.md
```

## Screenshots

<img width="1307" height="743" alt="Screenshot 2026-10-07 194851" src="https://github.com/user-attachments/assets/6c5b9c54-7a5e-4857-8d41-1f8f8394e48b" />
<img width="1310" height="736" alt="Screenshot 2026-10-07 194821" src="https://github.com/user-attachments/assets/bbdceeac-b687-49c2-a14f-c85dbfa8040b" />
<img width="1202" height="676" alt="Screenshot 2026-10-07 194758" src="https://github.com/user-attachments/assets/38c9760c-6825-4ee5-bb07-647c92441da7" />
<img width="1202" height="682" alt="Screenshot 2026-10-07 194737" src="https://github.com/user-attachments/assets/dfd2cda9-bba5-4450-9ce5-f4164cbb7ab6" />

## Future Improvements

- Add SHAP-based explainability for individual predictions.
- Retrain periodically on fresh data and track model drift.
- Add a cost-sensitive threshold (tie the risk cutoff to retention-offer cost
  vs. average customer lifetime value) instead of fixed probability bands.
- Automate the pipeline with a scheduler (e.g. Task Scheduler / cron) and
  push refreshed predictions straight into Power BI via a scheduled refresh.
