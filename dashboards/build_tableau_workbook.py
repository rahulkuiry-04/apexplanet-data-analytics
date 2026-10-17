from __future__ import annotations

import csv
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from tableauhyperapi import (
    Connection,
    CreateMode,
    HyperProcess,
    Inserter,
    Nullability,
    SqlType,
    TableDefinition,
    TableName,
    Telemetry,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "telco_churn_clean.csv"
OUTPUT_PATH = ROOT / "dashboards" / "customer_churn_dashboard.twbx"
EXTRACT_NAME = "Telco Customer Churn.hyper"
TABLE_NAME = "telco_churn"
DATASOURCE_NAME = "TelcoChurn"
DATASOURCE_CAPTION = "Telco Customer Churn"

INTEGER_COLUMNS = {"tenure", "churn_flag", "customer_count"}
REAL_COLUMNS = {"monthly_charges", "total_charges"}
SHEETS = (
    ("Churn Distribution", "churn", "customer_count", None),
    ("Churn by Contract", "contract", "churn_flag", None),
    ("Tenure vs Monthly Charges", "monthly_charges", "tenure", "churn"),
    ("Churn by Internet Service", "internet_service", "churn_flag", None),
)


def read_source() -> tuple[list[str], list[list[object]]]:
    with DATA_PATH.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError(f"No header row found in {DATA_PATH}")

        source_columns = reader.fieldnames
        columns = [*source_columns, "churn_flag", "customer_count"]
        rows: list[list[object]] = []

        for record in reader:
            row: list[object] = []
            for name in source_columns:
                value = record[name]
                if value == "":
                    row.append(None)
                elif name in INTEGER_COLUMNS:
                    row.append(int(value))
                elif name in REAL_COLUMNS:
                    row.append(float(value))
                else:
                    row.append(value)

            churn_flag = int(record["churn"] == "Yes")
            row.extend((churn_flag, 1))
            rows.append(row)

    return columns, rows


def create_extract(path: Path, columns: list[str], rows: list[list[object]]) -> None:
    table = TableDefinition(
        table_name=TableName("Extract", TABLE_NAME),
        columns=[
            TableDefinition.Column(
                name=name,
                type=(
                    SqlType.int()
                    if name in INTEGER_COLUMNS
                    else SqlType.double()
                    if name in REAL_COLUMNS
                    else SqlType.text()
                ),
                nullability=Nullability.NULLABLE,
            )
            for name in columns
        ],
    )

    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(
            endpoint=hyper.endpoint,
            database=str(path),
            create_mode=CreateMode.CREATE_AND_REPLACE,
        ) as connection:
            connection.catalog.create_schema("Extract")
            connection.catalog.create_table(table)
            with Inserter(connection, table) as inserter:
                inserter.add_rows(rows)
                inserter.execute()


def add_datasource(parent: ET.Element, columns: list[str]) -> None:
    datasource = ET.SubElement(
        parent,
        "datasource",
        {
            "caption": DATASOURCE_CAPTION,
            "inline": "true",
            "name": DATASOURCE_NAME,
            "version": "18.1",
        },
    )
    connection = ET.SubElement(
        datasource,
        "connection",
        {
            "class": "hyper",
            "dbname": f"Data/Extracts/{EXTRACT_NAME}",
            "schema": "Extract",
            "tablename": TABLE_NAME,
            "update-time": "",
        },
    )
    ET.SubElement(
        connection,
        "relation",
        {
            "name": TABLE_NAME,
            "table": f"[Extract].[{TABLE_NAME}]",
            "type": "table",
        },
    )

    column_container = ET.SubElement(datasource, "columns")
    for name in columns:
        is_measure = name in INTEGER_COLUMNS or name in REAL_COLUMNS
        datatype = (
            "integer"
            if name in INTEGER_COLUMNS
            else "real"
            if name in REAL_COLUMNS
            else "string"
        )
        ET.SubElement(
            column_container,
            "column",
            {
                "caption": name.replace("_", " ").title(),
                "datatype": datatype,
                "name": name,
                "role": "measure" if is_measure else "dimension",
                "type": "quantitative" if is_measure else "nominal",
            },
        )


def add_worksheet(parent: ET.Element, name: str, row_field: str, column_field: str, color_field: str | None) -> None:
    worksheet = ET.SubElement(parent, "worksheet", {"name": name})
    ET.SubElement(worksheet, "rows").text = f"[{row_field}]"
    ET.SubElement(worksheet, "cols").text = f"[{column_field}]"
    marks = ET.SubElement(worksheet, "marks")
    ET.SubElement(marks, "mark", {"class": "Automatic"})
    if color_field is not None:
        ET.SubElement(marks, "color").text = f"[{color_field}]"
    dependencies = ET.SubElement(worksheet, "datasource-dependencies")
    ET.SubElement(dependencies, "datasource", {"name": DATASOURCE_NAME})


def build_workbook(columns: list[str]) -> bytes:
    workbook = ET.Element(
        "workbook",
        {
            "original-version": "18.1",
            "source-build": "2024.1.0",
            "source-platform": "win",
            "version": "18.1",
        },
    )
    ET.SubElement(workbook, "preferences")
    datasources = ET.SubElement(workbook, "datasources")
    add_datasource(datasources, columns)

    worksheets = ET.SubElement(workbook, "worksheets")
    for name, row_field, column_field, color_field in SHEETS:
        add_worksheet(worksheets, name, row_field, column_field, color_field)

    dashboards = ET.SubElement(workbook, "dashboards")
    dashboard = ET.SubElement(dashboards, "dashboard", {"name": "Executive Dashboard"})
    ET.SubElement(dashboard, "size", {"height": "900", "type": "fixed", "width": "1400"})
    zones = ET.SubElement(dashboard, "zones")
    root_zone = ET.SubElement(
        zones,
        "zone",
        {
            "h": "100000",
            "id": "1",
            "type": "layout-basic",
            "w": "100000",
            "x": "0",
            "y": "0",
        },
    )
    for index, (name, _, _, _) in enumerate(SHEETS, start=2):
        column = (index - 2) % 2
        row = (index - 2) // 2
        ET.SubElement(
            root_zone,
            "zone",
            {
                "h": "49000",
                "id": str(index),
                "name": name,
                "w": "49000",
                "x": str(1000 + column * 50000),
                "y": str(1000 + row * 50000),
            },
        )

    ET.indent(workbook, space="  ")
    return ET.tostring(workbook, encoding="utf-8", xml_declaration=True)


def main() -> None:
    columns, rows = read_source()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary_directory:
        extract_path = Path(temporary_directory) / EXTRACT_NAME
        create_extract(extract_path, columns, rows)
        workbook_bytes = build_workbook(columns)

        with zipfile.ZipFile(OUTPUT_PATH, "w", compression=zipfile.ZIP_DEFLATED) as package:
            package.writestr("workbook.twb", workbook_bytes)
            package.write(extract_path, f"Data/Extracts/{EXTRACT_NAME}")

    with zipfile.ZipFile(OUTPUT_PATH) as package:
        if package.testzip() is not None:
            raise RuntimeError(f"Invalid file found in Tableau package: {OUTPUT_PATH}")

    print(f"Created {OUTPUT_PATH} with {len(rows):,} customers and {len(SHEETS)} worksheets.")


if __name__ == "__main__":
    main()
