"""Read-only file/hash and workbook join checks; not semantic PDF validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime import ContractError, digest, require


SHEETS = {
    "Handoff": "Record_ID", "Metadata": "Curve_ID", "Conditions": "Condition_ID",
    "Specifications": "Parameter_ID", "Pins": "Pin_ID", "Test_Circuits": "Record_ID",
    "Quality": "Quality_ID", "Curve_Data": "Point_ID", "Fitting_Data": "Fit_Point_ID",
    "Validation": "Test_ID",
}

HEADERS = {
    "Handoff": ["Category", "Key", "Value_Text", "Value_Number", "Status"],
    "Metadata": ["Graph_Sheet", "Condition_Group_ID", "Quality_ID", "Extraction_Status"],
    "Conditions": ["Condition_Group_ID", "Entity_Type", "Entity_ID", "Field", "Status"],
    "Specifications": ["Parameter", "Minimum", "Typical", "Maximum", "Condition_Group_ID", "Quality_ID"],
    "Pins": ["Device", "Package", "Physical_Pin", "Symbol", "Logical_Role", "Verification_Status"],
    "Test_Circuits": ["Circuit_ID", "Record_Type", "Status"],
    "Quality": ["Entity_Type", "Entity_ID", "Category", "Status"],
    "Curve_Data": ["Curve_ID", "Segment_ID", "Value_Status", "Quality_ID"],
    "Fitting_Data": ["Curve_ID", "Point_ID", "Role", "Fit_Eligible"],
    "Validation": ["Entity_Type", "Entity_ID", "Condition_Group_ID", "Circuit_ID", "Setup_Status", "Simulation_Status"],
}


def inspect_inputs(pdf, report, workbook, expected_part=None):
    paths = [Path(p).resolve() for p in (pdf, report, workbook)]
    for path in paths:
        require(path.is_file(), f"Required input missing: {path}")
    require(paths[0].suffix.lower() == ".pdf", "Complete PDF is required")
    with paths[0].open("rb") as stream:
        require(stream.read(5) == b"%PDF-", "Not a PDF file")
    required_report = paths[1].read_text(encoding="utf-8")
    require("NEEDED" in required_report and "Information Needed for the Behavioral Model" in required_report,
            "Unusable required-data report; semantic individual-item review is still required")
    try:
        import openpyxl
    except ImportError as exc:
        raise ContractError("openpyxl is required for workbook checks; no automatic installation") from exc
    wb = openpyxl.load_workbook(paths[2], read_only=True, data_only=False)
    try:
        require(set(SHEETS) <= set(wb.sheetnames), "Missing structured workbook sheets")
        data = {}
        ids = {}
        for sheet, id_field in SHEETS.items():
            rows = wb[sheet].iter_rows(values_only=True)
            headers = next(rows, ())
            require(headers and len(headers) == len(set(headers)), f"Empty/duplicate headers: {sheet}")
            require({id_field, *HEADERS[sheet]} <= set(headers), f"Missing contract headers: {sheet}")
            records = [dict(zip(headers, row)) for row in rows if any(v is not None for v in row)]
            values = [r[id_field] for r in records]
            require(all(isinstance(v, str) and v for v in values), f"Nontext/blank IDs: {sheet}")
            # Quality IDs may be reused to link multiple documented quality records.
            if sheet != "Quality":
                require(len(values) == len(set(values)), f"Duplicate IDs: {sheet}")
            ids[sheet], data[sheet] = set(values), records
            for r in records:
                require(not any(isinstance(v, str) and v.startswith("=") for v in r.values()),
                        f"Formula cells are prohibited: {sheet}/{r[id_field]}")
        handoff = data["Handoff"]
        require(any(str(r["Value_Text"]) == "1.0.0" and "schema" in str(r["Key"]).lower()
                    for r in handoff), "Unsupported or absent extraction schema")
        pdf_hash = digest(paths[0])
        require(any(str(r["Value_Text"]).lower() == pdf_hash and any(k in str(r["Key"]).lower() for k in ("hash", "sha"))
                    for r in handoff), "Workbook PDF hash does not match actual source")
        if expected_part:
            require(any(expected_part.casefold() in str(r["Value_Text"]).casefold()
                        and any(k in str(r["Key"]).lower() for k in ("part", "device", "target")) for r in handoff),
                    "Selected part not identified in workbook Handoff")
            require(expected_part.casefold() in required_report.casefold(), "Report selected part mismatch")
        groups = {r["Condition_Group_ID"] for r in data["Conditions"] if r["Condition_Group_ID"]}
        circuits = {r["Circuit_ID"] for r in data["Test_Circuits"] if r["Circuit_ID"]}
        for sheet, records in data.items():
            for r in records:
                for key, allowed in (("Condition_Group_ID", groups), ("Quality_ID", ids["Quality"]),
                                     ("Curve_ID", ids["Metadata"]), ("Point_ID", ids["Curve_Data"]), ("Circuit_ID", circuits)):
                    value = r.get(key)
                    if value and key != SHEETS[sheet]:
                        require(value in allowed, f"Broken {key}: {sheet}/{r[SHEETS[sheet]]}/{value}")
        point_curves = {r["Point_ID"]: r["Curve_ID"] for r in data["Curve_Data"]}
        for r in data["Fitting_Data"]:
            require(point_curves[r["Point_ID"]] == r["Curve_ID"], "Fit point references a different curve")
            if "holdout" in str(r["Role"]).lower() or "validation" in str(r["Role"]).lower():
                require(r["Fit_Eligible"] == 0, "Holdout must have Fit_Eligible=0")
        for r in data["Metadata"]:
            if r["Graph_Sheet"]:
                require(r["Graph_Sheet"] in wb.sheetnames, "Missing numerical graph sheet")
        for r in data["Validation"]:
            require(r["Simulation_Status"] == "not_run", "Extraction proposals are not completed simulations")
        return {"status": "structural_checks_passed", "sources": [
            {"path": str(p), "sha256": digest(p)} for p in paths],
            "record_counts": {s: len(rows) for s, rows in data.items()},
            "limitations": ["PDF completeness/readability and semantic target/condition/unit reconciliation require author review",
                            "Entity_Type aliases, composite schema columns and all extraction quality need semantic inspection"]}
    finally:
        wb.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--part")
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_inputs(args.pdf, args.report, args.workbook, args.part), indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "detail": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
