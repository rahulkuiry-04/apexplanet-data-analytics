from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "telco_churn_clean.csv"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

PDF_PATH = REPORTS_DIR / "Executive_Summary_Report.pdf"
LOGO_PATH = FIGURES_DIR / "apex_logo.png"
DONUT_PATH = FIGURES_DIR / "churn_distribution.png"
CONTRACT_PATH = FIGURES_DIR / "contract_churn.png"
PAYMENT_PATH = FIGURES_DIR / "payment_method_churn.png"
DASHBOARD_PATH = FIGURES_DIR / "dashboard_snapshot.png"


def build_logo() -> None:
    fig, ax = plt.subplots(figsize=(2.1, 2.1), dpi=220)
    circle = plt.Circle((0, 0), radius=1, color="#0ea5e9", alpha=0.2)
    ax.add_patch(circle)
    ax.text(0, 0, "AP", ha="center", va="center", fontsize=28, fontweight="bold", color="#e2e8f0")
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(LOGO_PATH, transparent=True, bbox_inches="tight")
    plt.close(fig)


def build_charts(df: pd.DataFrame) -> None:
    churn_counts = df["churn"].value_counts().reindex(["No", "Yes"]).fillna(0)
    labels = ["Retained", "Churned"]
    sizes = [int(churn_counts["No"]), int(churn_counts["Yes"])]
    colors_list = ["#22c55e", "#f97316"]

    fig, ax = plt.subplots(figsize=(4.2, 4.2), dpi=220)
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, wedgeprops={"edgecolor": "#0f172a", "linewidth": 1.5}, colors=colors_list)
    ax.set_title("Customer Retention vs Churn", fontsize=12, weight="bold", color="#0f172a")
    fig.tight_layout()
    fig.savefig(DONUT_PATH, facecolor="#f8fafc")
    plt.close(fig)

    contract_summary = (
        df.groupby("contract", observed=False)["churn"]
        .apply(lambda s: (s == "Yes").mean() * 100)
        .reset_index(name="churn_rate")
        .sort_values("churn_rate", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(5.8, 3.3), dpi=220)
    ax.bar(contract_summary["contract"], contract_summary["churn_rate"], color=["#2563eb", "#06b6d4", "#f59e0b"])
    ax.set_title("Churn Rate by Contract Type", fontsize=12, weight="bold", color="#0f172a")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_ylim(0, 50)
    for bar, val in zip(ax.patches, contract_summary["churn_rate"]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.5, f"{val:.1f}%", ha="center", va="bottom", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    fig.tight_layout()
    fig.savefig(CONTRACT_PATH, facecolor="#f8fafc")
    plt.close(fig)

    payment_summary = (
        df.groupby("payment_method", observed=False)["churn"]
        .apply(lambda s: (s == "Yes").mean() * 100)
        .reset_index(name="churn_rate")
        .sort_values("churn_rate", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(6.2, 3.3), dpi=220)
    ax.bar(payment_summary["payment_method"], payment_summary["churn_rate"], color=["#10b981", "#3b82f6", "#ef4444", "#8b5cf6"])
    ax.set_title("Churn Rate by Payment Method", fontsize=12, weight="bold", color="#0f172a")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_ylim(0, 50)
    for bar, val in zip(ax.patches, payment_summary["churn_rate"]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.4, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    plt.xticks(rotation=22, ha="right")
    fig.tight_layout()
    fig.savefig(PAYMENT_PATH, facecolor="#f8fafc")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4), dpi=220)
    axes[0].imshow(plt.imread(DONUT_PATH))
    axes[0].axis("off")
    axes[0].set_title("Retention overview", color="#0f172a", fontsize=10, pad=10)

    axes[1].imshow(plt.imread(CONTRACT_PATH))
    axes[1].axis("off")
    axes[1].set_title("Contract risk signal", color="#0f172a", fontsize=10, pad=10)

    fig.patch.set_facecolor("#f8fafc")
    fig.tight_layout()
    fig.savefig(DASHBOARD_PATH, facecolor="#f8fafc")
    plt.close(fig)


def make_story() -> list:
    df = pd.read_csv(DATA_PATH)
    churn_rate = (df["churn"] == "Yes").mean() * 100
    total_customers = len(df)
    avg_tenure = df["tenure"].mean()
    avg_monthly = df["monthly_charges"].mean()
    churn_by_contract = (
        df.groupby("contract", observed=False)["churn"]
        .apply(lambda s: (s == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )
    churn_by_payment = (
        df.groupby("payment_method", observed=False)["churn"]
        .apply(lambda s: (s == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )
    churn_by_internet = (
        df.groupby("internet_service", observed=False)["churn"]
        .apply(lambda s: (s == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#e2e8f0"),
        alignment=1,
        spaceAfter=12,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=colors.HexColor("#7dd3fc"),
        leading=16,
        spaceBefore=10,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#dfe7f5"),
        spaceAfter=8,
    )
    emphasis = ParagraphStyle(
        "Emphasis",
        parent=body,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#f8fafc"),
    )
    accent = ParagraphStyle(
        "Accent",
        parent=body,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#7dd3fc"),
    )

    narrative = [
        Paragraph("Apex Planet | Customer Churn Executive Summary", title_style),
        Spacer(1, 4 * mm),
        Paragraph("Day 39–40 | Executive Summary Report", ParagraphStyle("Sub", parent=body, fontSize=11, textColor=colors.HexColor("#94a3b8"), alignment=1, spaceAfter=12)),
        Spacer(1, 2 * mm),
        Table(
            [
                [Paragraph("Total customers", body), Paragraph(f"{total_customers:,}", emphasis)],
                [Paragraph("Churn rate", body), Paragraph(f"{churn_rate:.1f}%", emphasis)],
                [Paragraph("Average tenure", body), Paragraph(f"{avg_tenure:.1f} months", emphasis)],
                [Paragraph("Avg. monthly charge", body), Paragraph(f"${avg_monthly:.2f}", emphasis)],
            ],
            colWidths=[78 * mm, 60 * mm],
            hAlign="LEFT",
        ),
        Spacer(1, 6 * mm),
        Paragraph("Executive Summary", h2),
        Paragraph(
            "Apex Planet’s customer churn analysis indicates that 26.5% of the customer base is at risk of churn. "
            "The strongest drivers are contract design, internet service type, and payment behavior, with month-to-month contracts and fiber-optic plans showing materially higher churn risk than longer-term, lower-risk alternatives.",
            body,
        ),
        Paragraph(
            "The business implication is clear: retention interventions should prioritize customers on month-to-month contracts, fiber-optic service, and electronic check payments, while strengthening lifecycle programs for lower-tenure accounts. ",
            body,
        ),
        Paragraph("Key actions", h2),
        Paragraph("• Target at-risk customer segments with personalized retention offers and proactive outreach.", body),
        Paragraph("• Rework contract incentives to improve migration from month-to-month to one-year and two-year plans.", body),
        Paragraph("• Review telecom add-ons and payment friction to reduce churn triggers and improve customer satisfaction.", body),
        Spacer(1, 6 * mm),
        Paragraph("Table of contents", h2),
        Table(
            [
                [Paragraph("1. Executive Summary", body), Paragraph("1", body)],
                [Paragraph("2. Problem statement & objectives", body), Paragraph("2", body)],
                [Paragraph("3. Data source & methodology", body), Paragraph("2", body)],
                [Paragraph("4. Key findings & visuals", body), Paragraph("3", body)],
                [Paragraph("5. Statistical analysis", body), Paragraph("4", body)],
                [Paragraph("6. Recommendations", body), Paragraph("4", body)],
                [Paragraph("7. Future scope & limitations", body), Paragraph("4", body)],
            ],
            colWidths=[100 * mm, 20 * mm],
            hAlign="LEFT",
        ),
        PageBreak(),
        Paragraph("Problem statement & objectives", h2),
        Paragraph(
            "The core business problem is to identify why customers leave and which interventions are most likely to reduce churn. The analysis aims to quantify churn risk, isolate the strongest contributing variables, and translate findings into retention actions that can be operationalized by the commercial team.",
            body,
        ),
        Paragraph("Objectives", body),
        Paragraph("• Measure churn prevalence and segment risk by customer profile.", body),
        Paragraph("• Identify high-risk customer attributes and behavioral drivers.", body),
        Paragraph("• Prioritize the most impactful retention and offer strategies.", body),
        PageBreak(),
        Paragraph("Data source & methodology", h2),
        Paragraph(
            "Source: IBM Telco Customer Churn dataset, covering 7,043 customer records with 21 structured variables. Data was cleaned and standardized as part of the project workflow, including missing value handling, type normalization, and churn labeling. Statistical analysis used descriptive statistics, proportion comparisons, segmentation by contract, internet service, and payment method, and retention-churn comparisons across key factors.",
            body,
        ),
        Paragraph("Methodology", body),
        Paragraph("• Data ingestion and cleaning in Python using pandas.", body),
        Paragraph("• Risk profile comparisons by contract, internet service, and payment method.", body),
        Paragraph("• Customer behavior summary using tenure, monthly charges, and churn segmentation.", body),
        Paragraph("• Dashboard-style charting for executive readability and stakeholder review.", body),
        PageBreak(),
        Paragraph("Key findings & visuals", h2),
        Image(DASHBOARD_PATH, width=155 * mm, height=68 * mm),
        Spacer(1, 4 * mm),
        Paragraph("Top insight 1: Contract structure is the most important retention lever.", emphasis),
        Paragraph(f"Month-to-month contracts show a churn rate of {churn_by_contract.loc['Month-to-month']:.1f}%, versus {churn_by_contract.loc['One year']:.1f}% for one-year and {churn_by_contract.loc['Two year']:.1f}% for two-year contracts.", body),
        Paragraph("Top insight 2: Fiber optic customers churn at a much higher rate than DSL or no-internet customers.", body),
        Paragraph(f"Fiber optic customers face a churn rate of {churn_by_internet.loc['Fiber optic']:.1f}% compared with {churn_by_internet.loc['DSL']:.1f}% for DSL and {churn_by_internet.loc['No']:.1f}% for customers without internet service.", body),
        Paragraph("Top insight 3: Electronic-check payment is the highest-risk channel.", body),
        Paragraph(f"Customers paying by electronic check churn at {churn_by_payment.loc['Electronic check']:.1f}% versus {churn_by_payment.loc['Bank transfer (automatic)']:.1f}% for bank transfer and {churn_by_payment.loc['Credit card (automatic)']:.1f}% for credit card autopay.", body),
        Spacer(1, 4 * mm),
        Table(
            [[Image(DONUT_PATH, width=58 * mm, height=58 * mm), Image(CONTRACT_PATH, width=92 * mm, height=58 * mm)], [Image(PAYMENT_PATH, width=150 * mm, height=50 * mm)]],
            colWidths=[60 * mm, 90 * mm],
            style=[
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ],
        ),
        PageBreak(),
        Paragraph("Statistical analysis & recommendations", h2),
        Paragraph(
            f"The churn rate for the current customer base is {churn_rate:.1f}%, with churn concentrated in lower-tenure and higher-price segments. Average tenure among churned customers is {df.loc[df['churn'] == 'Yes', 'tenure'].mean():.1f} months, compared with {df.loc[df['churn'] == 'No', 'tenure'].mean():.1f} months among retained customers. Average monthly charges are ${df.loc[df['churn'] == 'Yes', 'monthly_charges'].mean():.2f} for churned customers and ${df.loc[df['churn'] == 'No', 'monthly_charges'].mean():.2f} for retained customers.",
            body,
        ),
        Paragraph("Recommendations", accent),
        Paragraph("1) Introduce retention offers for customers in month-to-month contracts and low-tenure cohorts.", body),
        Paragraph("2) Shift fiber-optic customers toward bundled plans with better service quality and value messaging.", body),
        Paragraph("3) Encourage autopay transitions away from electronic check to reduce churn risk and payment friction.", body),
        Paragraph("4) Monitor churn by segment monthly, using churn alerts to intervene before tenure drops below 12 months.", body),
        Paragraph("Future scope & limitations", accent),
        Paragraph(
            "This analysis is a cross-sectional snapshot and does not include time-based behavioral data, service tickets, or account-level interactions. Future work should incorporate historical retention events, campaign data, and machine-learning models for churn scoring and uplift analysis.",
            body,
        ),
    ]

    return narrative


def build_pdf() -> None:
    build_logo()
    df = pd.read_csv(DATA_PATH)
    build_charts(df)

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Apex Planet Executive Summary Report",
        author="Apex Planet Data Analytics",
    )

    styles = getSampleStyleSheet()
    dark_bg = colors.HexColor("#020817")
    accent = colors.HexColor("#38bdf8")
    text = colors.HexColor("#e2e8f0")

    def on_first_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(dark_bg)
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
        canvas.restoreState()
        canvas.saveState()
        canvas.drawImage(str(LOGO_PATH), 18 * mm, 260 * mm, width=18 * mm, height=18 * mm, mask='auto')
        canvas.setFillColor(accent)
        canvas.setFont("Helvetica-Bold", 18)
        canvas.drawString(44 * mm, 266 * mm, "APEX PLANET")
        canvas.setFillColor(text)
        canvas.setFont("Helvetica", 9)
        canvas.drawString(44 * mm, 260 * mm, "Customer Churn Intelligence")
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(18 * mm, 18 * mm, "Prepared for executive review")
        canvas.drawRightString(190 * mm, 18 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    def on_later_pages(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(dark_bg)
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
        canvas.restoreState()
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(190 * mm, 18 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    doc.build(make_story(), onFirstPage=on_first_page, onLaterPages=on_later_pages)


if __name__ == "__main__":
    build_pdf()
    print(f"Report created: {PDF_PATH}")
