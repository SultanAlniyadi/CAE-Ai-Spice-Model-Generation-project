"""Synthetic extraction-workbook contract checks, not PDF evidence validation."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_inputs as ci
import runtime as rt


@unittest.skipUnless(importlib.util.find_spec("openpyxl"), "openpyxl unavailable")
class InputTests(unittest.TestCase):
    def setUp(self):
        import openpyxl
        self.temporary = tempfile.TemporaryDirectory(prefix="source fixture ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.pdf = self.root / "source.pdf"
        self.pdf.write_bytes(b"%PDF-1.4\n% SYNTHETIC HEADER ONLY, NOT A READABLE DATASHEET\n")
        self.report = self.root / "report.md"
        self.report.write_text("SYNTHETIC\n## Information Needed for the Behavioral Model\nNEEDED synthetic item\n", encoding="utf-8")
        self.workbook = self.root / "evidence.xlsx"
        self.wb = openpyxl.Workbook()
        self.wb.remove(self.wb.active)
        for sheet, key in ci.SHEETS.items():
            self.wb.create_sheet(sheet).append([key, *ci.HEADERS[sheet]])
        self.wb["Handoff"].append(["schema", "identity", "schema", "1.0.0", None, "verified"])
        self.wb["Handoff"].append(["hash", "identity", "pdf_sha256", rt.digest(self.pdf), None, "verified"])
        self.wb["Handoff"].append(["target", "identity", "selected_part", "SYNTHETIC", None, "verified"])
        self.addCleanup(self.wb.close)

    def inspect(self):
        self.wb.save(self.workbook)
        return ci.inspect_inputs(self.pdf, self.report, self.workbook, "SYNTHETIC")

    def test_structural_check_disclaims_pdf_semantics(self):
        report = self.inspect()
        self.assertEqual(report["status"], "structural_checks_passed")
        self.assertTrue(report["limitations"])

    def test_missing_file_and_sheet(self):
        with self.assertRaises(rt.ContractError):
            ci.inspect_inputs(self.pdf, self.report, self.workbook)
        self.wb.remove(self.wb["Pins"])
        with self.assertRaises(rt.ContractError):
            self.inspect()

    def test_hash_mismatch(self):
        self.wb["Handoff"]["D3"] = "0" * 64
        with self.assertRaises(rt.ContractError):
            self.inspect()

    def test_wrong_schema_and_target(self):
        self.wb["Handoff"]["D2"] = "2.0.0"
        with self.assertRaises(rt.ContractError):
            self.inspect()
        self.wb["Handoff"]["D2"] = "1.0.0"
        self.wb["Handoff"]["D4"] = "OTHER_PART"
        with self.assertRaises(rt.ContractError):
            self.inspect()

    def test_broken_condition_join(self):
        self.wb["Specifications"].append(["parameter", "gain", None, 1, None, "missing_group", None])
        with self.assertRaises(rt.ContractError):
            self.inspect()

    def test_blank_is_not_zero(self):
        self.wb["Specifications"].append(["parameter", "offset", None, 0, None, None, None])
        self.assertEqual(self.inspect()["record_counts"]["Specifications"], 1)

    def test_holdout_leak_and_broken_point(self):
        self.wb["Metadata"].append(["curve", None, None, None, "readable"])
        self.wb["Curve_Data"].append(["point", "curve", "segment", "valid", None])
        self.wb["Fitting_Data"].append(["fit", "curve", "point", "holdout", 1])
        with self.assertRaises(rt.ContractError):
            self.inspect()
        self.wb["Fitting_Data"]["E2"] = 0
        self.inspect()
        self.wb["Fitting_Data"]["C2"] = "missing_point"
        with self.assertRaises(rt.ContractError):
            self.inspect()


if __name__ == "__main__":
    unittest.main()
