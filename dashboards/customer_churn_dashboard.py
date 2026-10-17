from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "telco_churn_clean.csv"
OUTPUT_PATH = ROOT / "dashboards" / "customer_churn_dashboard.html"


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["churn_flag"] = df["churn"].eq("Yes").astype(int)
    return df


def build_summary_cards(df: pd.DataFrame) -> str:
    total_customers = len(df)
    churn_rate = round(df["churn_flag"].mean() * 100, 1)
    avg_monthly = round(float(df["monthly_charges"].mean()), 2)
    avg_tenure = round(float(df["tenure"].mean()), 1)

    return f"""
    <div class="cards">
      <div class="card">
        <span class="label">Total customers</span>
        <span class="value">{total_customers:,}</span>
      </div>
      <div class="card">
        <span class="label">Churn rate</span>
        <span class="value">{churn_rate}%</span>
      </div>
      <div class="card">
        <span class="label">Avg. monthly charges</span>
        <span class="value">${avg_monthly:.2f}</span>
      </div>
      <div class="card">
        <span class="label">Avg. tenure</span>
        <span class="value">{avg_tenure} mo</span>
      </div>
    </div>
    """


def build_churn_donut(df: pd.DataFrame) -> go.Figure:
    churn_counts = df["churn"].value_counts().reindex(["No", "Yes"]).fillna(0)
    fig = px.pie(
        labels=["Retained", "Churned"],
        values=[int(churn_counts["No"]), int(churn_counts["Yes"])],
        hole=0.45,
        color_discrete_sequence=["#2ecc71", "#e74c3c"],
        title="Retention vs Churn",
    )
    fig.update_traces(textinfo="percent+label", hovertemplate="<b>%{label}</b><br>Customers: %{value}<extra></extra>")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=18, color="#dfe6f1"),
        font=dict(color="#dfe6f1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def build_contract_bar(df: pd.DataFrame) -> go.Figure:
    contract_summary = (
        df.groupby("contract", observed=False)["churn_flag"]
        .mean()
        .reset_index(name="churn_rate")
        .sort_values("churn_rate", ascending=False)
    )
    fig = px.bar(
        contract_summary,
        x="contract",
        y="churn_rate",
        color="contract",
        color_discrete_sequence=["#4f46e5", "#06b6d4", "#f59e0b"],
        title="Churn Rate by Contract Type",
        text=contract_summary["churn_rate"].map(lambda v: f"{v * 100:.1f}%"),
    )
    fig.update_traces(textposition="outside", hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.1%}<extra></extra>")
    fig.update_yaxes(tickformat=".0%", title="Churn rate")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=18, color="#dfe6f1"),
        font=dict(color="#dfe6f1"),
        legend_title_text="",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig


def build_tenure_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df,
        x="tenure",
        y="monthly_charges",
        color="churn",
        color_discrete_sequence=["#22c55e", "#ef4444"],
        hover_data=["customer_id", "contract", "internet_service"],
        title="Tenure vs Monthly Charges",
        opacity=0.7,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=18, color="#dfe6f1"),
        font=dict(color="#dfe6f1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig


def build_support_heatmap(df: pd.DataFrame) -> go.Figure:
    internet_contract = (
        df.groupby(["internet_service", "contract"], observed=False)["churn_flag"]
        .mean()
        .reset_index(name="churn_rate")
    )
    heat = internet_contract.pivot(index="internet_service", columns="contract", values="churn_rate").reindex(
        ["DSL", "Fiber optic", "No"],
        columns=["Month-to-month", "One year", "Two year"],
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=heat.values,
            x=list(heat.columns),
            y=list(heat.index),
            colorscale="RdYlGn_r",
            zmin=0,
            zmax=0.6,
            hovertemplate="<b>%{y}</b><br>%{x}<br>Churn rate: %{z:.1%}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Churn Rate by Internet Service and Contract",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=18, color="#dfe6f1"),
        font=dict(color="#dfe6f1"),
        xaxis=dict(showgrid=False, tickfont=dict(color="#dfe6f1")),
        yaxis=dict(showgrid=False, tickfont=dict(color="#dfe6f1")),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def style_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=18, color="#dfe6f1"),
        font=dict(color="#dfe6f1"),
        margin=dict(l=24, r=24, t=52, b=24),
        autosize=True,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.15)", zeroline=False)
    return fig


def churn_rate_by_category(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    summary = (
        df.groupby(column, observed=False)["churn_flag"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .rename("churn_rate")
        .reset_index()
    )
    fig = px.bar(
        summary,
        x=column,
        y="churn_rate",
        color="churn_rate",
        color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"],
        title=title,
        labels={column: column.replace("_", " ").title(), "churn_rate": "Churn rate (%)"},
        text=summary["churn_rate"].map(lambda value: f"{value:.1f}%"),
    )
    fig.update_traces(textposition="outside", hovertemplate="%{x}<br>Churn rate: %{y:.1f}%<extra></extra>")
    fig.update_coloraxes(showscale=False)
    return style_figure(fig)


def build_visualizations(df: pd.DataFrame) -> list[tuple[str, go.Figure]]:
    tenure_bands = pd.cut(
        df["tenure"],
        bins=[-1, 6, 12, 24, 48, 72],
        labels=["0–6 mo", "7–12 mo", "13–24 mo", "25–48 mo", "49–72 mo"],
    )
    tenure_summary = (
        df.assign(tenure_band=tenure_bands)
        .groupby("tenure_band", observed=False)["churn_flag"]
        .mean()
        .mul(100)
        .rename("churn_rate")
        .reset_index()
    )

    addon_columns = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]
    addon_data = df.melt(
        id_vars="churn_flag",
        value_vars=addon_columns,
        var_name="add_on",
        value_name="subscription",
    )
    addon_data = addon_data[addon_data["subscription"].isin(["Yes", "No"])]
    addon_summary = (
        addon_data.groupby(["add_on", "subscription"], observed=False)["churn_flag"]
        .mean()
        .mul(100)
        .rename("churn_rate")
        .reset_index()
    )
    addon_summary["add_on"] = addon_summary["add_on"].str.replace("_", " ").str.title()

    payment_mix = (
        df.groupby(["payment_method", "churn"], observed=False)
        .size()
        .rename("customers")
        .reset_index()
    )
    contract_charges = (
        df.groupby(["contract", "churn"], observed=False)["monthly_charges"]
        .mean()
        .reset_index()
    )

    return [
        ("Retention vs Churn", build_churn_donut(df)),
        ("Churn Rate by Contract Type", build_contract_bar(df)),
        ("Tenure vs Monthly Charges", build_tenure_scatter(df)),
        ("Churn by Service and Contract", build_support_heatmap(df)),
        ("Churn by Internet Service", churn_rate_by_category(df, "internet_service", "Churn Rate by Internet Service")),
        ("Churn by Payment Method", churn_rate_by_category(df, "payment_method", "Churn Rate by Payment Method")),
        ("Churn by Senior Citizen Status", churn_rate_by_category(df, "senior_citizen", "Churn Rate by Senior Citizen Status")),
        ("Churn by Partner Status", churn_rate_by_category(df, "partner", "Churn Rate by Partner Status")),
        ("Churn by Dependents", churn_rate_by_category(df, "dependents", "Churn Rate by Dependents")),
        ("Churn by Paperless Billing", churn_rate_by_category(df, "paperless_billing", "Churn Rate by Paperless Billing")),
        (
            "Churn Rate Across Add-on Services",
            style_figure(
                px.bar(
                    addon_summary,
                    x="add_on",
                    y="churn_rate",
                    color="subscription",
                    barmode="group",
                    title="Churn Rate Across Add-on Services",
                    labels={"add_on": "Add-on", "churn_rate": "Churn rate (%)", "subscription": "Subscribed"},
                    color_discrete_map={"Yes": "#22c55e", "No": "#ef4444"},
                )
            ),
        ),
        (
            "Tenure Distribution by Churn",
            style_figure(
                px.violin(
                    df,
                    x="churn",
                    y="tenure",
                    color="churn",
                    box=True,
                    points=False,
                    title="Tenure Distribution by Churn",
                    labels={"churn": "Churned", "tenure": "Tenure (months)"},
                    color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                )
            ),
        ),
        (
            "Monthly Charges Distribution",
            style_figure(
                px.histogram(
                    df,
                    x="monthly_charges",
                    color="churn",
                    barmode="overlay",
                    nbins=35,
                    opacity=0.72,
                    title="Monthly Charges Distribution by Churn",
                    labels={"monthly_charges": "Monthly charges ($)", "count": "Customers"},
                    color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                )
            ),
        ),
        (
            "Total Charges vs Tenure",
            style_figure(
                px.scatter(
                    df,
                    x="tenure",
                    y="total_charges",
                    color="churn",
                    opacity=0.65,
                    title="Total Charges vs Tenure",
                    labels={"tenure": "Tenure (months)", "total_charges": "Total charges ($)", "churn": "Churned"},
                    color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                )
            ),
        ),
        (
            "Churn Rate by Tenure Group",
            style_figure(
                px.bar(
                    tenure_summary,
                    x="tenure_band",
                    y="churn_rate",
                    title="Churn Rate by Tenure Group",
                    labels={"tenure_band": "Tenure group", "churn_rate": "Churn rate (%)"},
                    text=tenure_summary["churn_rate"].map(lambda value: f"{value:.1f}%"),
                    color="churn_rate",
                    color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"],
                )
            ),
        ),
        (
            "Customer Mix by Payment Method",
            style_figure(
                px.bar(
                    payment_mix,
                    x="payment_method",
                    y="customers",
                    color="churn",
                    barmode="group",
                    title="Customer Mix by Payment Method",
                    labels={"payment_method": "Payment method", "customers": "Customers", "churn": "Churned"},
                    color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                )
            ),
        ),
        (
            "Average Monthly Charges by Contract",
            style_figure(
                px.bar(
                    contract_charges,
                    x="contract",
                    y="monthly_charges",
                    color="churn",
                    barmode="group",
                    title="Average Monthly Charges by Contract",
                    labels={"contract": "Contract", "monthly_charges": "Average monthly charges ($)", "churn": "Churned"},
                    color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                )
            ),
        ),
        ("Churn by Gender", churn_rate_by_category(df, "gender", "Churn Rate by Gender")),
        (
            "Monthly Charges by Internet Service",
            style_figure(
                px.box(
                    df,
                    x="internet_service",
                    y="monthly_charges",
                    color="churn",
                    title="Monthly Charges by Internet Service",
                    labels={"internet_service": "Internet service", "monthly_charges": "Monthly charges ($)", "churn": "Churned"},
                    color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                )
            ),
        ),
        (
            "Average Tenure by Contract",
            style_figure(
                px.bar(
                    df.groupby(["contract", "churn"], observed=False)["tenure"]
                    .mean()
                    .rename("avg_tenure")
                    .reset_index(),
                    x="contract",
                    y="avg_tenure",
                    color="churn",
                    barmode="group",
                    title="Average Tenure by Contract and Churn",
                    labels={"contract": "Contract", "avg_tenure": "Average tenure (months)", "churn": "Churned"},
                    color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                )
            ),
        ),
    ]


def build_dashboard_html(df: pd.DataFrame) -> str:
    visualizations = build_visualizations(df)
    if len(visualizations) < 15:
        raise ValueError(f"Expected at least 15 Python visualizations; built {len(visualizations)}")
    cards = build_summary_cards(df)
    panels = [
        f'<div class="panel" data-visualization="{title}">{figure.to_html(full_html=False, include_plotlyjs=False)}</div>'
        for title, figure in visualizations
    ]

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Telco Customer Churn Dashboard</title>
      <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
      <style>
        :root {{
          --bg: #07111d;
          --panel: #0f1d2d;
          --panel-alt: #11273a;
          --border: rgba(148, 163, 184, 0.2);
          --text: #e2e8f0;
          --muted: #94a3b8;
          --primary: #4f46e5;
          --success: #22c55e;
          --danger: #ef4444;
          --secondary: #06b6d4;
        }}
        * {{ box-sizing: border-box; }}
        body {{
          margin: 0;
          font-family: "Segoe UI", sans-serif;
          background: radial-gradient(circle at top left, rgba(79,70,229,0.2), transparent 35%), var(--bg);
          color: var(--text);
        }}
        .container {{
          max-width: 1400px;
          margin: 0 auto;
          padding: 32px 24px 48px;
        }}
        h1 {{
          margin: 0 0 8px;
          font-size: clamp(2rem, 3vw, 3rem);
          letter-spacing: -0.04em;
        }}
        .subtitle {{
          margin: 0 0 24px;
          color: var(--muted);
          font-size: 1rem;
        }}
        .cards {{
          display: grid;
          grid-template-columns: repeat(4, minmax(180px, 1fr));
          gap: 18px;
          margin-bottom: 24px;
        }}
        .card {{
          background: linear-gradient(135deg, var(--panel), var(--panel-alt));
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 18px 20px;
          box-shadow: 0 12px 30px rgba(15, 23, 42, 0.25);
        }}
        .label {{
          display: block;
          color: var(--muted);
          font-size: 0.85rem;
          margin-bottom: 10px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
        }}
        .value {{
          font-size: clamp(1.6rem, 2.4vw, 2.3rem);
          font-weight: 700;
          color: #f8fafc;
        }}
        .grid {{
          display: grid;
          grid-template-columns: repeat(2, minmax(300px, 1fr));
          gap: 22px;
        }}
        .panel {{
          background: linear-gradient(180deg, rgba(15, 29, 45, 0.96), rgba(17, 39, 58, 0.88));
          border: 1px solid var(--border);
          border-radius: 18px;
          padding: 16px;
          box-shadow: 0 18px 40px rgba(2, 6, 23, 0.3);
          min-height: 380px;
        }}
        .panel .js-plotly-plot {{
          width: 100% !important;
          height: 100% !important;
        }}
        .brand {{
          display: flex;
          align-items: center;
          justify-content: center;
          margin-top: 28px;
          padding: 18px 20px;
          border-radius: 18px;
          border: 1px solid var(--border);
          background: linear-gradient(135deg, rgba(79,70,229,0.2), rgba(6,182,212,0.08));
          box-shadow: 0 12px 30px rgba(15, 23, 42, 0.25);
        }}
        .brand-mark {{
          font-size: 2.4rem;
          font-weight: 700;
          font-style: italic;
          letter-spacing: -0.06em;
          color: #f8fafc;
          margin-right: 12px;
        }}
        .brand-name {{
          font-size: 2.3rem;
          font-weight: 700;
          letter-spacing: -0.04em;
          color: #f8fafc;
        }}
        .brand-sub {{
          display: block;
          font-size: 0.82rem;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: var(--muted);
          text-align: center;
        }}
        @media (max-width: 980px) {{
          .cards {{ grid-template-columns: repeat(2, minmax(160px, 1fr)); }}
          .grid {{ grid-template-columns: 1fr; }}
          .brand-mark, .brand-name {{ font-size: 1.8rem; }}
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Telco Customer Churn Dashboard</h1>
        <p class="subtitle">Customer retention analysis for the ApexPlanet telecom dataset.</p>
        {cards}
        <div class="grid">
          {''.join(panels)}
        </div>
        <div class="brand">
          <div class="brand-mark">A</div>
          <div>
            <div class="brand-name">pexPlanet</div>
            <span class="brand-sub">Software Pvt. Ltd.</span>
          </div>
        </div>
      </div>
    </body>
    </html>
    """


def main() -> None:
    df = load_data(DATA_PATH)
    html = build_dashboard_html(df)
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Saved dashboard to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
