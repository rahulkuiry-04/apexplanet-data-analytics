-- Apexplanet Task 2: SQL fundamentals and business analysis (PostgreSQL)
-- Run after loading data/processed/telco_churn_clean.csv into telco_churn.
-- This is a one-time customer snapshot: monthly sales trends and product sales
-- cannot be derived because the dataset contains neither dates nor order lines.

-- 01. Select a few identifying and billing columns.
SELECT customer_id, tenure, contract, monthly_charges, churn
FROM telco_churn
LIMIT 10;

-- 02. Filter with WHERE.
SELECT customer_id, tenure, contract, monthly_charges
FROM telco_churn
WHERE tenure >= 12 AND churn = 'Yes';

-- 03. Sort and limit: highest monthly charges among churned customers.
SELECT customer_id, contract, monthly_charges
FROM telco_churn
WHERE churn = 'Yes'
ORDER BY monthly_charges DESC
LIMIT 10;

-- 04. INNER JOIN: compare all customers with the per-contract churn summary.
WITH churn_by_contract AS (
    SELECT contract,
           COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers
    FROM telco_churn
    GROUP BY contract
)
SELECT t.customer_id, t.contract, t.churn, c.churned_customers
FROM telco_churn AS t
INNER JOIN churn_by_contract AS c USING (contract)
ORDER BY t.customer_id
LIMIT 20;

-- 05. LEFT JOIN: retain every contract, including a summary with no match.
WITH contract_summary AS (
    SELECT contract, COUNT(*) AS customer_count
    FROM telco_churn
    GROUP BY contract
),
churn_summary AS (
    SELECT contract, COUNT(*) AS churned_customers
    FROM telco_churn
    WHERE churn = 'Yes'
    GROUP BY contract
)
SELECT c.contract, c.customer_count, s.churned_customers
FROM contract_summary AS c
LEFT JOIN churn_summary AS s USING (contract)
ORDER BY c.contract;

-- 06. RIGHT JOIN: same preservation result, with all contract rows on the right.
WITH churn_summary AS (
    SELECT contract, COUNT(*) AS churned_customers
    FROM telco_churn
    WHERE churn = 'Yes'
    GROUP BY contract
),
contract_summary AS (
    SELECT contract, COUNT(*) AS customer_count
    FROM telco_churn
    GROUP BY contract
)
SELECT c.contract, c.customer_count, s.churned_customers
FROM churn_summary AS s
RIGHT JOIN contract_summary AS c USING (contract)
ORDER BY c.contract;

-- 07. FULL OUTER JOIN: customers that are only in one of two cohorts.
WITH high_charge AS (
    SELECT customer_id, monthly_charges
    FROM telco_churn
    WHERE monthly_charges >= 90
),
long_tenure AS (
    SELECT customer_id, tenure
    FROM telco_churn
    WHERE tenure >= 60
)
SELECT COALESCE(h.customer_id, l.customer_id) AS customer_id,
       h.monthly_charges, l.tenure
FROM high_charge AS h
FULL OUTER JOIN long_tenure AS l USING (customer_id)
ORDER BY customer_id
LIMIT 30;

-- 08. Aggregate functions by contract.
SELECT contract,
       COUNT(*) AS customer_count,
       SUM(total_charges) AS lifetime_charges,
       AVG(monthly_charges) AS avg_monthly_charges,
       MIN(monthly_charges) AS min_monthly_charges,
       MAX(monthly_charges) AS max_monthly_charges
FROM telco_churn
GROUP BY contract
ORDER BY lifetime_charges DESC;

-- 09. HAVING: keep service groups with at least 500 customers.
SELECT internet_service, COUNT(*) AS customer_count
FROM telco_churn
GROUP BY internet_service
HAVING COUNT(*) >= 500
ORDER BY customer_count DESC;

-- 10. Churn rate by contract.
SELECT contract,
       COUNT(*) AS customer_count,
       COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
       ROUND(
           100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
           2
       ) AS churn_rate_pct
FROM telco_churn
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- 11. Churn rate by internet service.
SELECT internet_service,
       COUNT(*) AS customer_count,
       ROUND(
           100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
           2
       ) AS churn_rate_pct
FROM telco_churn
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;

-- 12. Subquery: customers paying more than the overall mean.
SELECT customer_id, contract, monthly_charges
FROM telco_churn
WHERE monthly_charges > (SELECT AVG(monthly_charges) FROM telco_churn)
ORDER BY monthly_charges DESC
LIMIT 20;

-- 13. CTE: top 10 customers by lifetime billed charges (revenue proxy).
WITH customer_revenue AS (
    SELECT customer_id, total_charges, tenure, contract
    FROM telco_churn
)
SELECT *
FROM customer_revenue
ORDER BY total_charges DESC
LIMIT 10;

-- 14. Retention rate by contract.
WITH contract_retention AS (
    SELECT contract,
           COUNT(*) AS customer_count,
           COUNT(*) FILTER (WHERE churn = 'No') AS retained_customers
    FROM telco_churn
    GROUP BY contract
)
SELECT contract, customer_count, retained_customers,
       ROUND(100.0 * retained_customers / customer_count, 2)
           AS retention_rate_pct
FROM contract_retention
ORDER BY retention_rate_pct DESC;

-- 15. Service-category performance (not product sales).
SELECT internet_service AS service_category,
       COUNT(*) AS customer_count,
       SUM(total_charges) AS lifetime_charges,
       ROUND(AVG(monthly_charges)::numeric, 2) AS avg_monthly_charges,
       ROUND(
           100.0 * COUNT(*) FILTER (WHERE churn = 'No') / COUNT(*),
           2
       ) AS retention_rate_pct
FROM telco_churn
GROUP BY internet_service
ORDER BY lifetime_charges DESC;

-- 16. ROW_NUMBER: rank customers within contract by lifetime charges.
SELECT customer_id, contract, total_charges,
       ROW_NUMBER() OVER (
           PARTITION BY contract ORDER BY total_charges DESC
       ) AS revenue_row_number
FROM telco_churn
ORDER BY contract, revenue_row_number
LIMIT 30;

-- 17. RANK: ties receive the same rank.
SELECT customer_id, contract, total_charges,
       RANK() OVER (
           PARTITION BY contract ORDER BY total_charges DESC
       ) AS revenue_rank
FROM telco_churn
ORDER BY contract, revenue_rank
LIMIT 30;

-- 18. LAG/LEAD: neighboring customer charge values by tenure (not time series).
SELECT customer_id, tenure, total_charges,
       LAG(total_charges) OVER (
           ORDER BY tenure, customer_id
       ) AS previous_row_charges,
       LEAD(total_charges) OVER (
           ORDER BY tenure, customer_id
       ) AS next_row_charges
FROM telco_churn
ORDER BY tenure, customer_id
LIMIT 30;

-- 19. Cumulative customer count across tenure months.
WITH tenure_counts AS (
    SELECT tenure, COUNT(*) AS customer_count
    FROM telco_churn
    GROUP BY tenure
)
SELECT tenure, customer_count,
       SUM(customer_count) OVER (
           ORDER BY tenure ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_customer_count
FROM tenure_counts
ORDER BY tenure;

-- 20. Five-tenure-row moving average of monthly charges.
WITH tenure_averages AS (
    SELECT tenure, AVG(monthly_charges) AS avg_monthly_charges
    FROM telco_churn
    GROUP BY tenure
)
SELECT tenure, avg_monthly_charges,
       AVG(avg_monthly_charges) OVER (
           ORDER BY tenure ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
       ) AS five_tenure_moving_average
FROM tenure_averages
ORDER BY tenure;

-- 21. Create/update a reusable summary view.
CREATE OR REPLACE VIEW telco_contract_summary AS
SELECT contract,
       COUNT(*) AS customer_count,
       ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
       ROUND(
           100.0 * COUNT(*) FILTER (WHERE churn = 'No') / COUNT(*),
           2
       ) AS retention_rate_pct
FROM telco_churn
GROUP BY contract;

-- 22. Query the view.
SELECT *
FROM telco_contract_summary
ORDER BY retention_rate_pct DESC;

-- 23. Inspect the execution plan before considering indexes.
EXPLAIN
SELECT customer_id, monthly_charges
FROM telco_churn
WHERE contract = 'One year' AND churn = 'No';

-- Optional candidate index (apply only after checking EXPLAIN and workload):
-- CREATE INDEX idx_telco_contract_churn
--     ON telco_churn (contract, churn);

-- 24. A monthly trend requires a dated fact table that this dataset does not have.
-- Example for a future sales table:
-- SELECT DATE_TRUNC('month', order_date) AS sales_month,
--        SUM(quantity * unit_price) AS revenue
-- FROM sales_order_lines
-- GROUP BY 1
-- ORDER BY 1;
