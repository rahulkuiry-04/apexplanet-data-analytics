# Apexplanet Data Analytics: Tasks 1–4

**Data Cleaning, Statistical Analysis, Forecasting, Customer Segmentation, Predictive Modeling, MySQL Data Extraction, and Interactive Dashboards**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)
![Database](https://img.shields.io/badge/Database-MySQL-blue)
![Status](https://img.shields.io/badge/Status-Tasks%201%E2%80%934%20Implemented-brightgreen)

## 📌 Project Overview

This project covers Tasks 1–4 of the Apexplanet Data Analytics program: setting up a reproducible analytics environment, cleaning and exploring a customer churn dataset, practicing SQL-based extraction with MySQL and Python, building interactive dashboards, and applying statistical analysis, forecasting, customer segmentation, and predictive modeling.

**Dataset analyzed:** IBM Telco Customer Churn (7,043 customers, 21 columns)
**Objective:** Identify the key factors associated with customer churn.
**Headline result:** 26.5% of customers churned, and contract type, tenure and internet service type were the strongest patterns.

Task 2 includes 20+ MySQL practice queries in [`sql/task2_queries.sql`](sql/task2_queries.sql), covering filtering, joins, aggregates, CTEs, subqueries, window functions, retention, reusable views, and `EXPLAIN`. The [`MySQL notebook`](notebooks/02_mysql_database.ipynb) integrates SQL with Python and Pandas for database connection, CSV loading, and automated query extraction using [`db_utils.py`](db_utils.py).

## 📁 Folder Structure

```
apexplanet-data-analytics/
├── data/
│   ├── raw/                # Original Telco data and separate daily temperature forecast sample
│   └── processed/          # Cleaned data (telco_churn_clean.csv)
├── notebooks/
│   ├── 02_mysql_database.ipynb  # Task 2: MySQL + Python practice
│   └── 03_advanced_analytics.ipynb # Task 4: statistics, time series, clustering and prediction
├── scripts/
│   └── 01_data_sourcing_and_cleaning.ipynb # Task 1: sourcing, cleaning and EDA
├── db_utils.py                  # MySQL connection, CSV loading and query helpers
├── sql/
│   └── task2_queries.sql        # MySQL practice queries, view and EXPLAIN
├── .env.example                 # MySQL settings template
├── requirements.txt
├── reports/
│   ├── cleaning_log.csv         # Log of every cleaning transformation
│   └── figures/                 # Saved EDA charts
├── dashboards/                  # Interactive dashboards and Tableau TWBX export
└── README.md
```

## ⚙️ Environment Setup

**Prerequisites:** [Anaconda](https://www.anaconda.com/download) or Miniconda, Git

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/apexplanet-data-analytics.git
cd apexplanet-data-analytics

# 2. Create and activate the environment
conda create -n analytics python=3.10 -y
conda activate analytics

# 3. Install dependencies
pip install -r requirements.txt
pip install jupyter ipykernel

# 4. Launch Jupyter
jupyter notebook
```

**Libraries used:** pandas, numpy, matplotlib, seaborn, plotly, scikit-learn, sqlalchemy, PyMySQL

## ✅ Task 2: SQL & Data Extraction

The MySQL practice covers `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `INNER`/`LEFT`/`RIGHT` joins, a MySQL-compatible `FULL OUTER JOIN` emulation, `GROUP BY`, `HAVING`, aggregate functions, subqueries, CTEs, and `ROW_NUMBER`, `RANK`, `LAG`, and `LEAD` window functions. Business-focused queries explore top customers by lifetime billed charges, retention and churn rates, and internet service category performance. The script also demonstrates a reusable view and query plan inspection with `EXPLAIN`; an optional index is documented for evaluation.

The notebook demonstrates connecting to MySQL, loading the cleaned CSV without overwriting an existing table, and extracting parameterized SQL results into Pandas DataFrames. See the [MySQL setup instructions](#task-2-mysql-setup) below.

### Task 2: MySQL setup

Create a MySQL database named `apexplanet`, copy `.env.example` to `.env`, and set your local connection credentials. Install project dependencies with `pip install -r requirements.txt`, then run `notebooks/02_mysql_database.ipynb`. The notebook loads `data/processed/telco_churn_clean.csv` into `telco_churn` (without replacing an existing table) and demonstrates SQL-to-Pandas extraction. Run the full query set in `sql/task2_queries.sql` with MySQL Workbench or the MySQL CLI.

The dataset has no transaction dates or order-line/product data. Monthly sales trends and product-category sales require a different dataset; the SQL practice instead analyzes customer retention, lifetime billed charges, recurring-charge snapshots, and internet service categories.

## 📊 Data Sources

| Item | Details |
|------|---------|
| **Dataset** | IBM Telco Customer Churn |
| **Source** | [Kaggle: Telco Customer Churn (IBM dataset)](https://www.kaggle.com/datasets/yeanzc/telco-customer-churn-ibm-dataset) |
| **File** | `data/raw/Telco-Customer-Churn.csv` |
| **Rows × Columns** | 7,043 × 21 |
| **Collection method** | Sample dataset published by IBM to demonstrate analytics tools; each row is one telecom customer |
| **Time period** | Single snapshot (no time dimension) |

**Known limitations:** The data is a fictional sample, so findings may not generalise to a real telecom company. It is a single snapshot with no dates, so trends over time can't be studied. It also has no location or customer-service history.

### Data Dictionary

| Column | Type (after cleaning) | Description |
|--------|------|-------------|
| `customer_id` | object | Unique customer identifier |
| `gender` | category | Male / Female |
| `senior_citizen` | category | Whether the customer is a senior citizen (Yes/No) |
| `partner` | category | Whether the customer has a partner |
| `dependents` | category | Whether the customer has dependents |
| `tenure` | int | Months the customer has stayed with the company |
| `phone_service` | category | Whether the customer has phone service |
| `multiple_lines` | category | Yes / No / No phone service |
| `internet_service` | category | DSL / Fiber optic / No |
| `online_security` | category | Online security add-on (Yes / No / No internet service) |
| `online_backup` | category | Online backup add-on |
| `device_protection` | category | Device protection add-on |
| `tech_support` | category | Tech support add-on |
| `streaming_tv` | category | Streaming TV add-on |
| `streaming_movies` | category | Streaming movies add-on |
| `contract` | category | Month-to-month / One year / Two year |
| `paperless_billing` | category | Whether the customer uses paperless billing |
| `payment_method` | category | Electronic check / Mailed check / Bank transfer (automatic) / Credit card (automatic) |
| `monthly_charges` | float | Amount charged per month |
| `total_charges` | float | Total amount charged over the customer's tenure |
| `churn` | category | **Target:** whether the customer left (Yes/No) |

## 🧹 Data Cleaning Summary

| Step | Action | Rows/Columns Affected |
|------|--------|-----------------------|
| Missing values | `total_charges` loaded as text because of blank strings; converted to numeric and filled the blanks with the median. All 11 affected customers have `tenure = 0` (brand-new customers) | 11 rows |
| Duplicates | Checked for exact duplicate rows; none found | 0 |
| Data types | `senior_citizen` mapped from 0/1 to No/Yes; text columns (except `customer_id`) converted to `category` | 17 columns |
| Outliers | IQR method (1.5×IQR) checked on `tenure`, `monthly_charges` and `total_charges`; no outliers found, so nothing was removed | 0 |
| Column names | Standardized to snake_case (e.g. `TotalCharges` → `total_charges`) | All 21 columns |

The full log is in [`reports/cleaning_log.csv`](reports/cleaning_log.csv), and the cleaned dataset (7,043 rows × 21 columns) is saved to `data/processed/telco_churn_clean.csv`.

## 🔍 Findings Summary

### Key Insights

1. **Contract type is the strongest driver of churn.** Month-to-month customers churn at **42.7%**, compared with **11.3%** on one-year contracts and **2.8%** on two-year contracts.
2. **New customers leave first.** The median tenure of churned customers is **10 months**, versus **38 months** for retained customers. Tenure has the strongest correlation with churn of the numeric features (r = **-0.35**).
3. **Higher bills and fiber optic service go with higher churn.** Churned customers pay **$74.4** per month on average versus **$61.3** for retained customers. Fiber optic customers churn at **41.9%**, against **19.0%** for DSL and **7.4%** for customers with no internet service.

### Patterns, Trends & Anomalies

- **Overall churn rate:** 26.5% (1,869 of 7,043 customers), so the target is moderately imbalanced.
- **Customer mix:** Month-to-month is the most common contract (3,875 customers), fiber optic is the most common internet service (3,096), and electronic check is the most common payment method (2,365).
- **Correlation with churn:** `tenure` -0.35, `total_charges` -0.20, `monthly_charges` 0.19, `senior_citizen` 0.15.
- **Strong overlap between features:** `tenure` and `total_charges` are strongly correlated (r = **0.83**), so using both together in a predictive model could add redundancy.
- **Data quality:** No duplicates and no IQR outliers. The only missing values were the 11 blank `total_charges` entries for customers with zero tenure.

### What this suggests

Retention effort is likely best aimed at **new, month-to-month customers**, especially those on **fiber optic** plans. Encouraging longer contracts looks like a promising lever. These are patterns in the data, not proven causes, and testing them would need further analysis.

### Visualizations

| | |
|---|---|
| ![Numeric distributions](reports/figures/hist_numeric.png) | ![Numeric boxplots](reports/figures/box_numeric.png) |
| ![Categorical counts](reports/figures/bar_categorical.png) | ![Tenure vs monthly charges](reports/figures/scatter_tenure_monthly.png) |
| ![Numeric features by churn](reports/figures/box_by_churn.png) | ![Correlation heatmap](reports/figures/correlation_heatmap.png) |

![Churn rate by category](reports/figures/churn_rate_by_category.png)

## 🚀 How to Reproduce

1. Complete the environment setup above.
2. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/yeanzc/telco-customer-churn-ibm-dataset) and place `Telco-Customer-Churn.csv` in `data/raw/`.
3. Open `scripts/01_data_sourcing_and_cleaning.ipynb` with the **Python (analytics)** kernel and run all cells.
4. Outputs are written to `data/processed/`, `reports/cleaning_log.csv` and `reports/figures/`.

## 📐 Task 4: Statistical Analysis and Modeling

Run [`notebooks/03_advanced_analytics.ipynb`](notebooks/03_advanced_analytics.ipynb) from top to bottom after installing `requirements.txt`. It covers descriptive statistics, confidence intervals, Welch's t-test, chi-square, one-way ANOVA, correlation-versus-causation cautions, customer segmentation with K-Means and PCA, churn classification, and a monthly-charge regression example. Metrics are computed from reproducible train/test splits; no accuracy or causal-impact claims are assumed in advance.

The Telco churn dataset is a single customer snapshot without dates, so it cannot support genuine time-series forecasting. To avoid treating customer tenure as calendar time or inventing observations, the notebook uses a separately sourced [daily minimum temperatures sample](https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv) for daily, weekly, and monthly resampling, decomposition, stationarity checks, smoothing, ARIMA/SARIMA forecasts, and held-out evaluation. These time-series results describe the weather sample, not Telco customers. The notebook reads a local `data/raw/daily-min-temperatures.csv` if present; otherwise, it retrieves the cited CSV, so an internet connection is needed on first run.

## 🗄️ Load the cleaned CSV into local MySQL

The MySQL workflow is in [`notebooks/02_mysql_database.ipynb`](notebooks/02_mysql_database.ipynb), with reusable connection, CSV-loading and query helpers in [`db_utils.py`](db_utils.py).

1. Install the project requirements, including the MySQL DBAPI driver:

   ```bash
   pip install -r requirements.txt
   ```

2. Create the target database in MySQL if it does not already exist:

   ```sql
   CREATE DATABASE apexplanet;
   ```

3. Copy `.env.example` to `.env` in the project root and set your local MySQL values there. `db_utils.py` loads this file when creating the engine. `.env` is ignored by Git, so keep the real password there and out of notebooks/source control:

   ```dotenv
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   DB_NAME=apexplanet
   ```

   Process environment variables with the same names take precedence over values from `.env`. Then launch Jupyter.

4. Open `notebooks/02_mysql_database.ipynb` and run its cells. It loads `data/processed/telco_churn_clean.csv` into `telco_churn`, checks the connection, then demonstrates a parameterized SQL query returned as a pandas DataFrame. The loader defaults to `if_exists="fail"` so it will not overwrite a table on rerun; choose `append` or `replace` explicitly only when appropriate.

## 📈 Executive Dashboard

The Python/Plotly dashboard in [`dashboards/customer_churn_dashboard.html`](dashboards/customer_churn_dashboard.html) contains **20 interactive visualizations** plus KPI cards. It covers churn and retention, contract and service segments, customer demographics, billing, add-on services, and tenure. Regenerate it after updating the cleaned dataset with:

```bash
python dashboards/customer_churn_dashboard.py
```

The native Power BI project is [`dashboards/powerbi/Customer Churn.pbip`](dashboards/powerbi/Customer%20Churn.pbip). It contains **19 report visuals across three pages**—Executive Overview, Customer Segments, and Billing and Retention—with customer, churn, contract, and billing measures plus contract and internet-service slicers. The project reads `data/processed/telco_churn_clean.csv`; rebuild it if the data or project root changes:

```bash
python dashboards/build_powerbi_project.py
```

Open the `.pbip` file in Power BI Desktop to inspect and edit the report. Use **Save As** in Power BI Desktop to create a `.pbix` copy. The packaged Tableau workbook is [`dashboards/customer_churn_dashboard.twbx`](dashboards/customer_churn_dashboard.twbx); it includes an embedded extract of the cleaned data. Regenerate it after changing the data with:

```bash
python dashboards/build_tableau_workbook.py
```

Open the `.twbx` file in Tableau Desktop or Tableau Public. It contains churn distribution, churn by contract and internet service, and tenure-versus-monthly-charges views.

## 🤖 Day 41–42: Automated Analytics Pipeline

The project now includes an automated analytics pipeline that performs the full end-to-end workflow:

- Extracts data from a CSV source by default (with optional support for database or API sources)
- Cleans and transforms the data
- Runs churn analytics and KPI calculations
- Exports the results to CSV and optional Excel files
- Sends an email summary report when SMTP settings are configured
- Can be scheduled using Windows Task Scheduler, GitHub Actions, or Apache Airflow

### Run the pipeline locally

```bash
python scripts/automate_analytics_pipeline.py
```

Optional flags:

```bash
python scripts/automate_analytics_pipeline.py \
  --source-type csv \
  --source-path data/processed/telco_churn_clean.csv \
  --output-dir reports/automation \
  --report-name churn_analytics_report \
  --send-email
```

### Database or API source options

```bash
python scripts/automate_analytics_pipeline.py \
  --source-type database \
  --db-url mysql+pymysql://user:password@localhost:3306/apexplanet \
  --sql-query "SELECT * FROM telco_churn"
```

```bash
python scripts/automate_analytics_pipeline.py \
  --source-type api \
  --api-url "https://example.com/api/churn-data"
```

### Scheduling options

1. Windows Task Scheduler
   - Create a basic task and point it to `python.exe`
   - Add the script path as an argument, for example:
     `C:\Rahul\Apex_Planet\scripts\automate_analytics_pipeline.py`
   - Set a daily or weekly trigger based on business needs

2. GitHub Actions
   - Add a workflow that runs the script on a cron schedule
   - Store SMTP and email credentials in GitHub Secrets

3. Apache Airflow
   - Build a DAG that executes the Python script daily or weekly
   - Use Airflow variables or environment secrets for upstream data sources and email credentials

### Output files

The pipeline writes results to `reports/automation/` including:

- `churn_analytics_report_summary.csv`
- `churn_analytics_report_contract_churn.csv`
- `churn_analytics_report_internet_churn.csv`
- `churn_analytics_report_payment_churn.csv`
- optional `churn_analytics_report_results.xlsx` when Excel dependencies are available

## 📊 Day 43–45: Final Dashboard & GitHub Documentation

This phase focuses on finalizing the analytics outputs and preparing the project for portfolio and GitHub presentation.

### Final dashboard update

The dashboard has been updated with the final churn insights and visual storytelling driven by the business findings:

- retention vs churn distribution
- churn by contract type
- tenure vs monthly charges
- churn by internet service and payment method
- filterable and presentation-ready dashboard structure for stakeholder review

The primary dashboard artifact is:

- [dashboards/customer_churn_dashboard.html](dashboards/customer_churn_dashboard.html)
- [dashboards/customer_churn_dashboard.py](dashboards/customer_churn_dashboard.py)

To regenerate the dashboard locally:

```bash
python dashboards/customer_churn_dashboard.py
```

### Publish to a cloud platform

#### Option 1: Power BI Service

1. Open the cleaned dataset in Power BI Desktop.
2. Import the processed file from `data/processed/telco_churn_clean.csv`.
3. Recreate the key visuals: churn rate, contract trends, internet service churn, and payment method analysis.
4. Publish the report to Power BI Service.
5. Configure scheduled refresh and share the dashboard with stakeholders.

#### Option 2: Tableau Public

1. Connect Tableau Desktop to the cleaned dataset.
2. Build the same visuals with filters and KPI cards.
3. Publish the workbook to Tableau Public.
4. Share the dashboard link in the GitHub project README or portfolio.

### GitHub documentation standards

This repository is organized for professional portfolio use and GitHub presentation:

- clear project overview and business context
- reproducible setup instructions
- dataset and methodology summary
- code and notebook structure
- dashboard and report artifacts
- business findings and recommended actions
- automation and scheduling guidance

### Repository documentation checklist

- README describes the business problem and outcome
- setup, dependencies, and environment are documented
- outputs and artifacts are clearly linked
- dashboard/demo links are included
- meaningful insights are summarized for non-technical stakeholders
- scheduling or automation workflows are covered

## 🧾 Task 5: Final Reporting, Deployment & Presentation

### ApexPlanet Data Analytics Project

**Objective:** Analyze the Telco customer churn dataset to identify the strongest churn drivers, validate the key patterns with statistical evidence, and present a business-ready solution for retention strategy.

**Dataset description:** The project uses an IBM Telco Customer Churn sample dataset with 7,043 customer records and 21 variables covering demographics, contract type, service usage, billing behavior, and churn status.

**Key questions answered:**
- What are the strongest patterns associated with churn?
- Which customer segments are most at risk?
- Which business levers are most likely to reduce churn?

**Tech Stack:**
- Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly
- SQL and MySQL workflows
- Power BI / Tableau
- scikit-learn, statsmodels

**Project Structure:**
- `/notebooks/` - EDA, SQL workflow, analytics and modeling
- `/scripts/` - automation and preprocessing scripts
- `/data/` - raw and processed datasets
- `/dashboards/` - HTML, Power BI, and Tableau deliverables
- `/reports/` - charts, logs, and summary exports

**Key Findings:**
1. Contract type is the strongest driver of churn: month-to-month customers churn at a much higher rate than one-year and two-year customers.
2. Newer customers churn more often than long-tenure customers, making early retention a critical business lever.
3. Fiber optic plans and electronic check payments are associated with materially higher churn risk.

**Dashboard Link:**
- [Power BI / Tableau Public link](#) — update with the deployed dashboard URL when published

**How to Run:**
1. Clone the project repository.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the notebooks in order to clean, query, and analyze the data.
4. Regenerate the dashboard with `python dashboards/customer_churn_dashboard.py`.

**Author:**
- Rahul Kuiry
- Apexplanet Software Pvt. Ltd. Internship

---

This task finalizes the project as a professional, stakeholder-ready analytics deliverable with a clear business narrative, reproducible methods, and actionable deployment guidance.

## 🛠️ Next Steps

- Explore additional relationships (add-on services, payment method and demographics vs churn).
- Build a churn prediction model, handling the class imbalance and the `tenure` / `total_charges` overlap.
- Extend the dashboard with filters, drill-down views, or a deployment-ready web app.
- Add a CI/CD workflow to run the pipeline automatically in production.

## 👤 Author

**Rahul Kuiry**
📧 rahulkuiry04@gmail.com
🔗 [LinkedIn](https://www.linkedin.com/in/rahul-kuiry-419049261/) | 🔗  [GitHub](https://github.com/rahulkuiry-04/)

---
*Completed as part of the Apexplanet Data Analytics Internship, Tasks 1–4.*