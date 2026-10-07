-- ============================================================================
-- analysis.sql — 20 business questions answered in MySQL
-- Run after database.sql and importing cleaned_customer_churn.csv.
-- Valid MySQL 8.0 syntax. Every query has a comment stating the business
-- question it answers.
-- ============================================================================

USE churn_analytics;

-- 1. Total customers in the base
SELECT COUNT(*) AS total_customers FROM customers;

-- 2. Total churned customers
SELECT COUNT(*) AS total_churned FROM customers WHERE Churn = 'Yes';

-- 3. Overall churn rate (%)
SELECT
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customers;

-- 4. Non-churn (retention) rate (%)
SELECT
    ROUND(SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS retention_rate_pct
FROM customers;

-- 5. Average monthly charge across all customers
SELECT ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charge FROM customers;

-- 6. Average total charges across all customers
SELECT ROUND(AVG(TotalCharges), 2) AS avg_total_charges FROM customers;

-- 7. Total monthly recurring revenue across the customer base
SELECT ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue FROM customers;

-- 8. Monthly revenue at risk (revenue currently coming from already-churned customers)
SELECT ROUND(SUM(MonthlyCharges), 2) AS monthly_revenue_at_risk
FROM customers
WHERE Churn = 'Yes';

-- 9. Churn rate by contract type
SELECT
    Contract,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- 10. Churn rate by payment method
SELECT
    PaymentMethod,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;

-- 11. Churn rate by internet service type
SELECT
    InternetService,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;

-- 12. Churn rate by tenure group (uses the TenureGroup feature created in feature_engineering.py)
SELECT
    TenureGroup,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY TenureGroup
ORDER BY FIELD(TenureGroup, '0-12', '13-24', '25-48', '49-60', '60+');

-- 13. Churn rate by senior citizen status
SELECT
    CASE WHEN SeniorCitizen = 1 THEN 'Senior' ELSE 'Non-Senior' END AS customer_group,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY customer_group;

-- 14. High-value churned customers (top 20 by TotalCharges among churned)
SELECT customerID, Contract, tenure, MonthlyCharges, TotalCharges
FROM customers
WHERE Churn = 'Yes'
ORDER BY TotalCharges DESC
LIMIT 20;

-- 15. Customers with high monthly charges (above the 90th percentile threshold, approximated here as > 90)
SELECT customerID, Contract, MonthlyCharges, Churn
FROM customers
WHERE MonthlyCharges > 90
ORDER BY MonthlyCharges DESC;

-- 16. Customers with low tenure (<= 6 months) — newest, highest-risk cohort
SELECT customerID, tenure, Contract, MonthlyCharges, Churn
FROM customers
WHERE tenure <= 6
ORDER BY tenure ASC;

-- 17. Churn rate by payment method + contract combined (finds the worst-performing combination)
SELECT
    PaymentMethod,
    Contract,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY PaymentMethod, Contract
HAVING COUNT(*) >= 20   -- ignore tiny/noisy segments
ORDER BY churn_rate_pct DESC
LIMIT 10;

-- 18. Average revenue (MonthlyCharges) by churn status
SELECT
    Churn,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(TotalCharges), 2) AS avg_total_charges
FROM customers
GROUP BY Churn;

-- 19. Top customer segments with highest churn (Contract + InternetService combined)
SELECT
    Contract,
    InternetService,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY Contract, InternetService
HAVING COUNT(*) >= 20
ORDER BY churn_rate_pct DESC
LIMIT 10;

-- 20. Final management/business summary — one-row executive snapshot
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS monthly_revenue_at_risk,
    ROUND(AVG(tenure), 1) AS avg_tenure_months
FROM customers;