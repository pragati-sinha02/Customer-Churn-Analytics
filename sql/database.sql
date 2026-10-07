-- ============================================================================
-- database.sql
-- Creates the database and table for the cleaned Telco Customer Churn data.
-- Column types match the ACTUAL cleaned_customer_churn.csv schema produced
-- by python/data_cleaning.py + python/feature_engineering.py.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS churn_analytics;
USE churn_analytics;

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customerID          VARCHAR(20) PRIMARY KEY,
    gender               VARCHAR(10),
    SeniorCitizen        TINYINT,
    Partner              VARCHAR(5),
    Dependents           VARCHAR(5),
    tenure               INT,
    PhoneService         VARCHAR(5),
    MultipleLines        VARCHAR(20),
    InternetService      VARCHAR(20),
    OnlineSecurity       VARCHAR(5),
    OnlineBackup         VARCHAR(5),
    DeviceProtection     VARCHAR(5),
    TechSupport          VARCHAR(5),
    StreamingTV          VARCHAR(5),
    StreamingMovies      VARCHAR(5),
    Contract             VARCHAR(20),
    PaperlessBilling     VARCHAR(5),
    PaymentMethod        VARCHAR(30),
    MonthlyCharges       DECIMAL(8,2),
    TotalCharges         DECIMAL(10,2),
    Churn                VARCHAR(5),
    TenureGroup          VARCHAR(10),
    AvgMonthlySpend      DECIMAL(8,2),
    NumAddOnServices     TINYINT,
    IsNewCustomer        TINYINT,
    HasMultipleServices  TINYINT
);

-- ============================================================================
-- HOW TO IMPORT THE CSV (MySQL Workbench — beginner-friendly path)
-- ============================================================================
-- 1. Open MySQL Workbench and connect to your local MySQL instance
--    (default connection is usually "Local instance MySQL", port 3306).
-- 2. Open this file (database.sql) as a new SQL tab: File -> Open SQL Script.
-- 3. Click the lightning-bolt "Execute" icon (or Ctrl+Shift+Enter) to run
--    everything above and create the database + empty table.
-- 4. In the left sidebar, expand "churn_analytics" -> right-click "customers"
--    -> "Table Data Import Wizard".
-- 5. Browse to: Customer-Churn-Analytics/data/cleaned_customer_churn.csv
-- 6. Choose "Use existing table: customers", keep default column mapping
--    (the CSV headers match the column names above), then click Next -> Next -> Finish.
-- 7. Verify the import worked by running the query below.
-- ============================================================================

-- Verification query — should return 7043 (or however many rows your cleaned CSV has)
SELECT COUNT(*) AS total_rows_imported FROM customers;

-- Quick sanity check on the target column
SELECT Churn, COUNT(*) AS count_per_class FROM customers GROUP BY Churn;