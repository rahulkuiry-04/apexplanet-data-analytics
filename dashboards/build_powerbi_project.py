from __future__ import annotations

import csv
import json
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "telco_churn_clean.csv"
OUTPUT_DIR = ROOT / "dashboards" / "powerbi"
PROJECT_NAME = "Customer Churn"
MODEL_NAME = f"{PROJECT_NAME}.SemanticModel"
REPORT_NAME = f"{PROJECT_NAME}.Report"
TABLE_NAME = "Telco Churn"

MEASURES = {
    "Total Customers": ("COUNTROWS('Telco Churn')", "#,0"),
    "Churned Customers": (
        "CALCULATE([Total Customers], 'Telco Churn'[churn] = \"Yes\")",
        "#,0",
    ),
    "Churn Rate": ("DIVIDE([Churned Customers], [Total Customers])", "0.0%"),
    "Average Tenure": ("AVERAGE('Telco Churn'[tenure])", "0.0"),
    "Average Monthly Charges": ("AVERAGE('Telco Churn'[monthly_charges])", "$#,0.00"),
    "Total Charges": ("SUM('Telco Churn'[total_charges])", "$#,0"),
}

PAGE_SPECS: list[tuple[str, list[dict[str, Any]]]] = [
    (
        "Executive Overview",
        [
            {"type": "card", "measure": "Total Customers", "x": 20, "y": 20, "w": 250, "h": 110},
            {"type": "card", "measure": "Churn Rate", "x": 290, "y": 20, "w": 250, "h": 110},
            {"type": "card", "measure": "Average Monthly Charges", "x": 560, "y": 20, "w": 300, "h": 110},
            {"type": "card", "measure": "Average Tenure", "x": 880, "y": 20, "w": 250, "h": 110},
            {
                "type": "pieChart",
                "category": "churn",
                "measure": "Total Customers",
                "x": 20,
                "y": 155,
                "w": 530,
                "h": 300,
            },
            {
                "type": "clusteredBarChart",
                "category": "contract",
                "measure": "Churn Rate",
                "x": 570,
                "y": 155,
                "w": 580,
                "h": 300,
            },
            {
                "type": "clusteredColumnChart",
                "category": "internet_service",
                "measure": "Churn Rate",
                "x": 20,
                "y": 475,
                "w": 530,
                "h": 280,
            },
            {
                "type": "lineChart",
                "category": "tenure",
                "measure": "Churn Rate",
                "x": 570,
                "y": 475,
                "w": 580,
                "h": 280,
            },
        ],
    ),
    (
        "Customer Segments",
        [
            {"type": "slicer", "category": "contract", "x": 20, "y": 20, "w": 240, "h": 160},
            {"type": "slicer", "category": "internet_service", "x": 280, "y": 20, "w": 260, "h": 160},
            {
                "type": "clusteredBarChart",
                "category": "payment_method",
                "measure": "Churn Rate",
                "x": 20,
                "y": 200,
                "w": 540,
                "h": 300,
            },
            {
                "type": "clusteredColumnChart",
                "category": "senior_citizen",
                "measure": "Churn Rate",
                "x": 580,
                "y": 20,
                "w": 560,
                "h": 300,
            },
            {
                "type": "clusteredBarChart",
                "category": "partner",
                "measure": "Churn Rate",
                "x": 580,
                "y": 340,
                "w": 560,
                "h": 300,
            },
            {
                "type": "clusteredColumnChart",
                "category": "dependents",
                "measure": "Churn Rate",
                "x": 20,
                "y": 520,
                "w": 540,
                "h": 260,
            },
        ],
    ),
    (
        "Billing and Retention",
        [
            {
                "type": "clusteredColumnChart",
                "category": "paperless_billing",
                "measure": "Churn Rate",
                "x": 20,
                "y": 20,
                "w": 540,
                "h": 280,
            },
            {
                "type": "clusteredBarChart",
                "category": "contract",
                "measure": "Average Monthly Charges",
                "x": 580,
                "y": 20,
                "w": 560,
                "h": 280,
            },
            {
                "type": "clusteredColumnChart",
                "category": "gender",
                "measure": "Churn Rate",
                "x": 20,
                "y": 320,
                "w": 540,
                "h": 280,
            },
            {
                "type": "clusteredBarChart",
                "category": "internet_service",
                "measure": "Total Charges",
                "x": 580,
                "y": 320,
                "w": 560,
                "h": 280,
            },
            {
                "type": "tableEx",
                "columns": ["contract", "internet_service", "churn"],
                "x": 20,
                "y": 620,
                "w": 1120,
                "h": 180,
            },
        ],
    ),
]


def read_columns() -> tuple[list[str], list[str]]:
    with DATA_PATH.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError(f"No header row found in {DATA_PATH}")
        return reader.fieldnames, [column for column in reader.fieldnames]


def power_query_source(columns: list[str]) -> str:
    path = str(DATA_PATH).replace("\\", "\\\\").replace('"', '""')
    typed = []
    for column in columns:
        if column == "tenure":
            type_name = "Int64.Type"
        elif column in {"monthly_charges", "total_charges"}:
            type_name = "Currency.Type"
        else:
            type_name = "type text"
        typed.append(f'{{"{column}", {type_name}}}')

    lines = [
        "let",
        f'Source = Csv.Document(File.Contents("{path}"), '
        f'[Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", '
        f"{{{', '.join(typed)}}})",
        "in",
        '    #"Changed Type"',
    ]
    return "\n".join(f"\t\t\t\t\t{line}" for line in lines)


def make_semantic_model(columns: list[str]) -> None:
    model_dir = OUTPUT_DIR / MODEL_NAME
    definition_dir = model_dir / "definition"
    tables_dir = definition_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    (model_dir / "definition.pbism").write_text(
        json.dumps({"version": "4.0", "settings": {}}, indent=2) + "\n",
        encoding="utf-8",
    )
    (definition_dir / "database.tmdl").write_text("database\n\tcompatibilityLevel: 1550\n", encoding="utf-8")

    model_lines = [
        "model Model",
        "\tculture: en-US",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tsourceQueryCulture: en-US",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        '\tannotation __PBI_TimeIntelligenceEnabled = 0',
        '\tannotation PBI_QueryOrder = ["Telco Churn"]',
        "",
        f"\tref table '{TABLE_NAME}'",
        "\tref cultureInfo en-US",
        "",
    ]
    (definition_dir / "model.tmdl").write_text("\n".join(model_lines), encoding="utf-8")

    column_types = {
        "tenure": ("int64", "0"),
        "monthly_charges": ("double", "$#,0.00"),
        "total_charges": ("double", "$#,0.00"),
    }
    table_lines = [f"table '{TABLE_NAME}'", f"\tlineageTag: {uuid.uuid4()}"]
    for column in columns:
        data_type, format_string = column_types.get(column, ("string", ""))
        summarize_by = "average" if column == "tenure" else "sum" if column in column_types else "none"
        table_lines.extend(
            [
                "",
                f"\tcolumn '{column}'",
                f"\t\tdataType: {data_type}",
                f"\t\tlineageTag: {uuid.uuid4()}",
            ]
        )
        if format_string:
            table_lines.append(f"\t\tformatString: {format_string}")
        table_lines.extend(
            [
                f"\t\tsummarizeBy: {summarize_by}",
                f"\t\tsourceColumn: {column}",
                "",
                "\t\tannotation SummarizationSetBy = Automatic",
            ]
        )

    for name, (expression, format_string) in MEASURES.items():
        table_lines.extend(
            [
                "",
                f"\tmeasure '{name}' = {expression}",
                f"\t\tformatString: {format_string}",
                "\t\tdisplayFolder: Key Metrics",
                f"\t\tlineageTag: {uuid.uuid4()}",
            ]
        )

    table_lines.extend(
        [
            "",
            f"\tpartition '{TABLE_NAME}' = m",
            "\t\tmode: import",
            "\t\tsource =",
            power_query_source(columns),
            "",
            "\tannotation PBI_NavigationStepName = Navigation",
            "\tannotation PBI_ResultType = Table",
            "",
        ]
    )
    (tables_dir / f"{TABLE_NAME}.tmdl").write_text("\n".join(table_lines), encoding="utf-8")


def column_expression(field_name: str) -> dict[str, Any]:
    return {
        "Column": {
            "Expression": {"SourceRef": {"Source": "t"}},
            "Property": field_name,
        }
    }


def measure_expression(measure_name: str) -> dict[str, Any]:
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Source": "t"}},
            "Property": measure_name,
        }
    }


def query_select(field_name: str, measure: bool = False) -> dict[str, Any]:
    expression = measure_expression(field_name) if measure else column_expression(field_name)
    field_ref = f"{TABLE_NAME}.{field_name}"
    return {
        **expression,
        "Name": field_ref,
        "NativeReferenceName": field_name.replace("_", " ").title(),
    }


def visual_container(spec: dict[str, Any], ordinal: int) -> dict[str, Any]:
    visual_type = spec["type"]
    projections: dict[str, list[dict[str, Any]]] = {}
    select: list[dict[str, Any]] = []
    if visual_type in {"card"}:
        measure = spec["measure"]
        query_ref = f"{TABLE_NAME}.{measure}"
        projections["Values"] = [{"queryRef": query_ref, "active": True}]
        select.append(query_select(measure, measure=True))
    elif visual_type == "tableEx":
        fields = spec["columns"]
        projections["Values"] = []
        for field in fields:
            query_ref = f"{TABLE_NAME}.{field}"
            projections["Values"].append({"queryRef": query_ref, "active": True})
            select.append(query_select(field))
    elif visual_type == "slicer":
        field = spec["category"]
        query_ref = f"{TABLE_NAME}.{field}"
        projections["Values"] = [{"queryRef": query_ref, "active": True}]
        select.append(query_select(field))
    else:
        category = spec["category"]
        query_ref = f"{TABLE_NAME}.{category}"
        projections["Category"] = [{"queryRef": query_ref, "active": True}]
        select.append(query_select(category))
        if visual_type == "pieChart":
            projections["Legend"] = [{"queryRef": query_ref, "active": True}]
            projections["Values"] = [{"queryRef": f"{TABLE_NAME}.{spec['measure']}", "active": True}]
            select.append(query_select(spec["measure"], measure=True))
        else:
            projections["Y"] = [{"queryRef": f"{TABLE_NAME}.{spec['measure']}", "active": True}]
            select.append(query_select(spec["measure"], measure=True))

    name = uuid.uuid4().hex[:20]
    config = {
        "name": name,
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": spec["x"],
                    "y": spec["y"],
                    "z": ordinal * 1000,
                    "width": spec["w"],
                    "height": spec["h"],
                    "tabOrder": ordinal,
                },
            }
        ],
        "singleVisual": {
            "visualType": visual_type,
            "projections": projections,
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "t", "Entity": TABLE_NAME, "Type": 0}],
                "Select": select,
            },
            "drillFilterOtherVisuals": True,
        },
    }
    return {
        "config": json.dumps(config, separators=(",", ":")),
        "filters": "[]",
        "height": spec["h"],
        "width": spec["w"],
        "x": spec["x"],
        "y": spec["y"],
        "z": ordinal * 1000,
    }


def make_report() -> None:
    report_dir = OUTPUT_DIR / REPORT_NAME
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "definition.pbir").write_text(
        json.dumps(
            {
                "version": "4.0",
                "datasetReference": {"byPath": {"path": f"../{MODEL_NAME}"}},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    sections = []
    for page_index, (page_name, visuals) in enumerate(PAGE_SPECS):
        page_id = f"ReportSection{uuid.uuid4().hex[:20]}"
        sections.append(
            {
                "config": "{}",
                "displayName": page_name,
                "displayOption": 1,
                "filters": "[]",
                "height": 900,
                "name": page_id,
                "ordinal": page_index,
                "visualContainers": [visual_container(spec, index + 1) for index, spec in enumerate(visuals)],
                "width": 1280,
            }
        )

    report = {
        "config": json.dumps(
            {
                "version": "5.59",
                "themeCollection": {
                    "baseTheme": {"name": "CY24SU10", "version": "5.61", "type": 2}
                },
                "activeSectionIndex": 0,
                "defaultDrillFilterOtherVisuals": True,
            },
            separators=(",", ":"),
        ),
        "layoutOptimization": 0,
        "resourcePackages": [],
        "sections": sections,
    }
    (report_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    project = {
        "version": "1.0",
        "artifacts": [{"report": {"path": REPORT_NAME}}],
        "settings": {"enableAutoRecovery": True},
    }
    (OUTPUT_DIR / f"{PROJECT_NAME}.pbip").write_text(
        json.dumps(project, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}")
    columns, _ = read_columns()
    make_semantic_model(columns)
    make_report()
    visual_count = sum(len(visuals) for _, visuals in PAGE_SPECS)
    print(f"Created Power BI project with {len(PAGE_SPECS)} pages and {visual_count} report visuals:")
    print(OUTPUT_DIR / f"{PROJECT_NAME}.pbip")


if __name__ == "__main__":
    main()
