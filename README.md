"# apexplanet-data-analytics" 
# Apexplanet Data Analytics: Task 1

**Foundational Setup & Exploratory Data Analysis (EDA)**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

## 📌 Project Overview

This project is Task 1 of the Apexplanet Data Analytics program. It covers setting up a reproducible analytics environment, sourcing and cleaning a real-world dataset, and performing exploratory data analysis (EDA) to uncover patterns, trends, and anomalies.

**Dataset analyzed:** [Dataset name, e.g. IBM Telco Customer Churn]
**Objective:** [One sentence, e.g. Identify the key factors associated with customer churn.]

## 📁 Folder Structure

```
apexplanet-data-analytics/
├── data/
│   ├── raw/            # Original, unmodified datasets
│   └── processed/      # Cleaned data ready for analysis
├── notebooks/          # Jupyter notebooks (EDA and documentation)
├── scripts/            # Reusable Python scripts
├── reports/            # PDF/PPT summaries
├── dashboards/         # Power BI / Tableau files (PBIX/TWBX)
├── environment.yml     # Conda environment specification
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
conda install -y pandas numpy matplotlib seaborn plotly scikit-learn sqlalchemy jupyter ipykernel

# Or recreate the exact environment:
# conda env create -f environment.yml

# 4. Launch Jupyter
jupyter notebook
```

**Libraries used:** pandas, numpy, matplotlib, seaborn, plotly, scikit-learn, sqlalchemy

## 📊 Data Sources

| Item | Details |
|------|---------|
| **Dataset** | [Name] |
| **Source** | [Kaggle / Our World in Data / IBM / Tableau / Company] ([link]) |
| **Rows × Columns** | [e.g. 7,043 × 21] |
| **Collection method** | [How the data was originally collected] |
| **Time period** | [If applicable] |

**Known limitations:** [e.g. Snapshot data with no time dimension; possible sampling bias; some fields self-reported.]

### Data Dictionary (key columns)

| Column | Type | Description |
|--------|------|-------------|
| [column_1] | [int/float/category/datetime] | [Description] |
| [column_2] | [type] | [Description] |

## 🧹 Data Cleaning Summary

| Step | Action | Rows/Columns Affected |
|------|--------|-----------------------|
| Missing values | [e.g. Filled `TotalCharges` with median] | [11 rows] |
| Duplicates | [Removed exact duplicates] | [0] |
| Data types | [Converted `date` to datetime] | [1 column] |
| Outliers | [IQR method, capped at 1.5×IQR] | [n rows] |
| Column names | [Standardized to snake_case] | [All] |

The full cleaning log is documented in `notebooks/01_eda.ipynb`.

## 🔍 Findings Summary

### Key Insights

1. **[Insight 1]:** [e.g. Customers on month-to-month contracts churn at 3× the rate of those on two-year contracts.]
2. **[Insight 2]:** [Description with supporting numbers.]
3. **[Insight 3]:** [Description with supporting numbers.]

### Patterns, Trends & Anomalies

- [Pattern or trend observed]
- [Notable correlation, e.g. tenure and total charges: r = 0.83]
- [Anomaly or outlier worth flagging]

### Visualizations

![Correlation Heatmap](reports/figures/correlation_heatmap.png)
![Distribution Plot](reports/figures/distribution.png)

## 🚀 How to Reproduce

1. Complete the environment setup above.
2. Place the raw dataset in `data/raw/`.
3. Open `notebooks/01_eda.ipynb` and run all cells.
4. Cleaned output is saved to `data/processed/`.

## 🛠️ Next Steps

- [Task 2: e.g. SQL analysis / dashboarding]
- [Further feature engineering or modeling ideas]

## 👤 Author

**Rahul Kuiry**
📧 rahulkuiry04@gmail.com
🔗 [LinkedIn](https://linkedin.com/in/<your-handle>) | [GitHub](https://github.com/<your-username>)

---
*Completed as part of the Apexplanet Data Analytics Internship, Task 1.*