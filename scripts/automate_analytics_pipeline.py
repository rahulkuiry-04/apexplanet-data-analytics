from __future__ import annotations

import argparse
import json
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any
from urllib import request

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = ROOT / "data" / "processed" / "telco_churn_clean.csv"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "automation"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate the Apex Planet churn analytics pipeline.")
    parser.add_argument("--source-type", choices=["csv", "database", "api"], default="csv", help="Data source type.")
    parser.add_argument("--source-path", default=str(DEFAULT_CSV_PATH), help="CSV file path for the source dataset.")
    parser.add_argument("--db-url", default=os.getenv("DATABASE_URL"), help="Database URL for database-backed extraction.")
    parser.add_argument("--api-url", default=os.getenv("API_URL"), help="API endpoint returning JSON for extraction.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Where to export generated files.")
    parser.add_argument("--report-name", default="churn_analytics_report", help="Base file name for outputs.")
    parser.add_argument("--sql-query", default=None, help="Optional SQL query to run when source-type=database.")
    parser.add_argument("--send-email", action="store_true", help="Send a summary email after export.")
    parser.add_argument("--smtp-host", default=os.getenv("SMTP_HOST"), help="SMTP host for email delivery.")
    parser.add_argument("--smtp-port", default=os.getenv("SMTP_PORT", "587"), help="SMTP port.")
    parser.add_argument("--smtp-user", default=os.getenv("SMTP_USERNAME"), help="SMTP username.")
    parser.add_argument("--smtp-password", default=os.getenv("SMTP_PASSWORD"), help="SMTP password.")
    parser.add_argument("--email-from", default=os.getenv("EMAIL_FROM"), help="Sender address.")
    parser.add_argument("--email-to", default=os.getenv("EMAIL_TO"), help="Recipient address.")
    return parser.parse_args()


def load_environment() -> None:
    load_dotenv(ROOT / ".env")


def extract_data(args: argparse.Namespace) -> pd.DataFrame:
    if args.source_type == "csv":
        return pd.read_csv(args.source_path)

    if args.source_type == "database":
        if not args.db_url:
            raise ValueError("A database URL is required when --source-type database is used.")
        engine = create_engine(args.db_url)
        if args.sql_query:
            return pd.read_sql(args.sql_query, engine)
        table_name = "telco_churn"
        return pd.read_sql_table(table_name, con=engine)

    if args.source_type == "api":
        if not args.api_url:
            raise ValueError("An API URL is required when --source-type api is used.")
        req = request.Request(args.api_url, headers={"User-Agent": "ApexPlanetAnalytics/1.0"})
        with request.urlopen(req, timeout=30) as response:
            payload = response.read().decode("utf-8")
        data = json.loads(payload)
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict):
            for key in ["results", "data", "records"]:
                if isinstance(data.get(key), list):
                    return pd.DataFrame(data[key])
            return pd.json_normalize(data)
        raise ValueError("The API response was not in a supported JSON format.")

    raise ValueError(f"Unsupported source type: {args.source_type}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    working_df = df.copy()
    working_df.columns = [str(column).strip().lower().replace(" ", "_") for column in working_df.columns]

    if "total_charges" in working_df.columns:
        working_df["total_charges"] = pd.to_numeric(working_df["total_charges"], errors="coerce")
        median_total = working_df["total_charges"].median()
        working_df["total_charges"] = working_df["total_charges"].fillna(median_total)

    if "tenure" in working_df.columns:
        working_df["tenure"] = pd.to_numeric(working_df["tenure"], errors="coerce").fillna(0).astype(int)

    if "monthly_charges" in working_df.columns:
        working_df["monthly_charges"] = pd.to_numeric(working_df["monthly_charges"], errors="coerce")

    if "senior_citizen" in working_df.columns:
        working_df["senior_citizen"] = working_df["senior_citizen"].replace({0: "No", 1: "Yes"})

    if "churn" in working_df.columns:
        working_df["churn"] = working_df["churn"].astype(str).str.strip().str.title()
        working_df["churn_flag"] = working_df["churn"].eq("Yes").astype(int)

    if "customer_id" in working_df.columns:
        working_df["customer_id"] = working_df["customer_id"].astype(str)

    working_df = working_df.drop_duplicates().reset_index(drop=True)
    return working_df


def build_summary(df: pd.DataFrame) -> dict[str, Any]:
    total_customers = len(df)
    churn_rate = round(float(df["churn_flag"].mean() * 100), 2) if "churn_flag" in df.columns else 0.0
    avg_monthly = round(float(df["monthly_charges"].mean()), 2) if "monthly_charges" in df.columns else 0.0
    avg_tenure = round(float(df["tenure"].mean()), 2) if "tenure" in df.columns else 0.0

    summary = {
        "total_customers": int(total_customers),
        "churn_rate_pct": churn_rate,
        "avg_monthly_charges": avg_monthly,
        "avg_tenure_months": avg_tenure,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if "contract" in df.columns:
        summary["churn_by_contract"] = (
            df.groupby("contract", observed=False)["churn_flag"].mean().mul(100).round(2).sort_values(ascending=False).to_dict()
        )

    if "internet_service" in df.columns:
        summary["churn_by_internet_service"] = (
            df.groupby("internet_service", observed=False)["churn_flag"].mean().mul(100).round(2).sort_values(ascending=False).to_dict()
        )

    if "payment_method" in df.columns:
        summary["churn_by_payment_method"] = (
            df.groupby("payment_method", observed=False)["churn_flag"].mean().mul(100).round(2).sort_values(ascending=False).to_dict()
        )

    return summary


def export_results(df: pd.DataFrame, summary: dict[str, Any], output_dir: Path, report_name: str) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}

    summary_df = pd.DataFrame([summary])
    summary_path = output_dir / f"{report_name}_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    files["summary"] = str(summary_path)

    if "contract" in df.columns:
        contract_df = (
            df.groupby("contract", observed=False)["churn_flag"]
            .mean()
            .mul(100)
            .rename("churn_rate_pct")
            .reset_index()
        )
        contract_path = output_dir / f"{report_name}_contract_churn.csv"
        contract_df.to_csv(contract_path, index=False)
        files["contract"] = str(contract_path)

    if "internet_service" in df.columns:
        internet_df = (
            df.groupby("internet_service", observed=False)["churn_flag"]
            .mean()
            .mul(100)
            .rename("churn_rate_pct")
            .reset_index()
        )
        internet_path = output_dir / f"{report_name}_internet_churn.csv"
        internet_df.to_csv(internet_path, index=False)
        files["internet"] = str(internet_path)

    if "payment_method" in df.columns:
        payment_df = (
            df.groupby("payment_method", observed=False)["churn_flag"]
            .mean()
            .mul(100)
            .rename("churn_rate_pct")
            .reset_index()
        )
        payment_path = output_dir / f"{report_name}_payment_churn.csv"
        payment_df.to_csv(payment_path, index=False)
        files["payment"] = str(payment_path)

    try:
        excel_path = output_dir / f"{report_name}_results.xlsx"
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            if "contract" in df.columns:
                contract_df.to_excel(writer, sheet_name="Contract", index=False)
            if "internet_service" in df.columns:
                internet_df.to_excel(writer, sheet_name="Internet", index=False)
            if "payment_method" in df.columns:
                payment_df.to_excel(writer, sheet_name="Payment", index=False)
        files["excel"] = str(excel_path)
    except Exception:
        files["excel"] = "Excel export skipped: openpyxl is not installed. CSV exports are ready."

    return files


def send_email(summary: dict[str, Any], files: dict[str, str], args: argparse.Namespace) -> None:
    if not args.send_email:
        return

    required = [args.smtp_host, args.smtp_user, args.smtp_password, args.email_from, args.email_to]
    if any(value in (None, "") for value in required):
        raise ValueError("SMTP details are missing. Provide them via arguments or environment variables.")

    body = f"""
    <html>
      <body style="font-family: Arial; color: #0f172a;">
        <h2>Apex Planet Analytics Pipeline</h2>
        <p>Pipeline run completed successfully.</p>
        <ul>
          <li>Total customers: {summary['total_customers']}</li>
          <li>Churn rate: {summary['churn_rate_pct']}%</li>
          <li>Average monthly charges: ${summary['avg_monthly_charges']}</li>
          <li>Average tenure: {summary['avg_tenure_months']} months</li>
        </ul>
        <p>Files generated:</p>
        <ul>
          {''.join(f'<li>{path}</li>' for path in files.values() if path and not path.startswith('Excel export skipped'))}
        </ul>
      </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["Subject"] = "Apex Planet analytics pipeline report"
    msg["From"] = args.email_from
    msg["To"] = args.email_to
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(args.smtp_host, int(args.smtp_port)) as server:
        server.starttls()
        server.login(args.smtp_user, args.smtp_password)
        server.send_message(msg)


def main() -> None:
    load_environment()
    args = parse_args()
    df = extract_data(args)
    cleaned = clean_data(df)
    summary = build_summary(cleaned)
    output_dir = Path(args.output_dir)
    files = export_results(cleaned, summary, output_dir, args.report_name)

    if args.send_email:
        send_email(summary, files, args)

    print(json.dumps({"summary": summary, "files": files}, indent=2))


if __name__ == "__main__":
    main()
