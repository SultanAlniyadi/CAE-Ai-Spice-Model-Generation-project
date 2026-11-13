"""Synthetic contract/harness tests; no real device validation claims."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import runtime as rt


def criterion(kind="interval", **values):
    return {"kind": kind, "unit": "V", "basis": "approved_budget",
            "approval": {"by": "synthetic test", "reference": "not a device approval"},
            "provenance": [{"source_id": "source", "locator": "synthetic fixture"}], **values}


def make_suite(root, family="operational_amplifier", analysis="op"):
    root.mkdir()
    refs = [{"source_id": "source", "locator": "synthetic pin/limit fixture"}]
    interface = {"subcircuit": "DUT", "status": "accepted", "approval": {"by": "test", "reference": "fixture"},
                 "terminals": [{"name": "IN", "role": "input", "pin_ids": ["pin1"], "channel": "single"},
                               {"name": "OUT", "role": "output", "pin_ids": ["pin2"], "channel": "single"}],
                 "source_refs": refs}
    (root / "interface.json").write_text(json.dumps(interface), encoding="utf-8")
    (root / "benches").mkdir()
    (root / "benches" / "test.py").write_text(
        "def build_deck(model_path, interface, test):\n"
        "    return '* Synthetic only\\n.include \\\"' + str(model_path) + '\\\"\\nXtest in out DUT\\n.end\\n'\n"
        "def measure(run_dir, test):\n"
        "    return {'value': 1.0, 'unit': 'V'}\n", encoding="utf-8")
    shutil.copy2(SCRIPTS / "runtime.py", root / "runtime.py")
    shutil.copy2(SCRIPTS.parent / "templates" / "run_suite.py", root / "run_suite.py")
    test = {"id": "test_core", "requirement_ids": ["req"], "description": "Synthetic core check",
            "behavior": "synthetic transfer", "applicability": "synthetic only", "priority": "critical",
            "acceptance_role": "blocking", "role_reason": "synthetic core", "readiness": "ready",
            "prerequisites": [], "analysis": analysis, "conditions": {"supply_V": 2},
            "stimulus": {"input_V": 1}, "fixture": {"load_ohm": 1000},
            "metric": {"name": "output", "unit": "V", "definition": "settled output",
                       "window": {"kind": "operating_point"}, "resolution": {"min_samples": 1}},
            "criterion": criterion(min=0.9, max=1.1), "source_refs": refs, "reference_files": [],
            "evidence_role": "functional", "bench": "benches/test.py", "timeout_s": 10,
            "simulation_status": "not_run"}
    manifest = {"schema_version": "1.0.0", "suite_id": "synthetic", "suite_version": "fixture-1",
                "family": family, "target": {"part": "SYNTHETIC", "variant": "none", "package": "none",
                                            "grade": "none", "channel": "single", "scope": "harness only"},
                "sources": [{"id": "source", "kind": "synthetic", "sha256": "0" * 64,
                             "revision": "fixture", "locator": "synthetic fixture"}],
                "interface_file": "interface.json",
                "simulator": {"backend": "ngspice_batch", "required_features": [], "timeout_s": 10},
                "requirements": [{"id": "req", "description": "synthetic", "source_refs": refs,
                                  "mandatory": True, "core": True}],
                "coverage": [{"requirement_id": "req", "test_ids": ["test_core"], "disposition": "covered",
                              "reason": "synthetic coverage"}], "tests": [test], "hashes": {},
                "assumptions": [], "blockers": [], "harness_validation": {"status": "not_run", "evidence_files": []}}
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


class CriteriaTests(unittest.TestCase):
    def check_value(self, c, value):
        return rt.evaluate({"value": value, "unit": "V"}, c)["status"]

    def test_inclusive_bounds_and_sign(self):
        for value in (-1, 0, 1):
            self.assertEqual(self.check_value(criterion(min=-1, max=1), value), "pass")
        self.assertEqual(self.check_value(criterion(min=-1, max=1), 1.001), "fail")
        self.assertEqual(self.check_value(criterion("minimum", min=0), 0), "pass")
        self.assertEqual(self.check_value(criterion("maximum", max=-1), 0), "fail")

    def test_absolute_and_relative_zero_floor(self):
        self.assertEqual(self.check_value(criterion("absolute_error", reference=-1, tolerance=0.5), -0.5), "pass")
        self.assertEqual(self.check_value(criterion("relative_error", reference=0, tolerance=0.1, zero_floor=1), 0.05), "pass")
        with self.assertRaises(rt.ContractError):
            self.check_value(criterion("relative_error", reference=0, tolerance=0.1, zero_floor=0), 0)

    def test_invalid_measurements(self):
        for value in (None, True, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(rt.ContractError):
                self.check_value(criterion(min=0, max=1), value)
        with self.assertRaises(rt.ContractError):
            rt.evaluate({"value": 1, "unit": "A"}, criterion(min=0, max=1))
        with self.assertRaises(rt.ContractError):
            rt.evaluate({"value": 1, "unit": "V", "valid": False}, criterion(min=0, max=1))

    def test_curve_phase_wrap_and_rms(self):
        c = criterion("curve_error", reference=[179, -179], tolerance=2, reduction="max", period=360)
        self.assertEqual(rt.evaluate({"values": [-179, 179], "unit": "V"}, c)["status"], "pass")
        c.update(reference=[0, 0], tolerance=1, reduction="rms", period=None)
        self.assertEqual(rt.evaluate({"values": [0, 1], "unit": "V"}, c)["status"], "pass")
        with self.assertRaises(rt.ContractError):
            rt.evaluate({"values": [0], "unit": "V"}, c)

    def test_invalid_bounds_and_budget(self):
        for c in (criterion(min=2, max=1), criterion(min=False, max=1),
                  criterion("absolute_error", reference=0, tolerance=-1)):
            with self.assertRaises(rt.ContractError):
                rt.validate_criterion(c)
        c = criterion(min=0, max=1)
        del c["approval"]
        with self.assertRaises(rt.ContractError):
            rt.validate_criterion(c)

    def test_event_measurements_and_resolution(self):
        self.assertEqual(rt.crossing([0, 1, 2], [0, 1, 2], 0.5, "rising", 0, 2, 3, 1), 0.5)
        self.assertEqual(rt.crossing([0, 1, 2], [2, 1, 0], 1.5, "falling", 0, 2, 3, 1), 0.5)
        for y, step in (([0, 0, 0], 1), ([0, 1, 2], 0.1)):
            with self.assertRaises(rt.ContractError):
                rt.crossing([0, 1, 2], y, 0.5, "rising", 0, 2, 3, step)
        self.assertEqual(rt.settling_time([0, 1, 2, 3], [0, 1, 1, 1], 0, 1, 0.1, 1, 3, 4, 1), 1)
        with self.assertRaises(rt.ContractError):
            rt.settling_time([0, 1, 2, 3], [0, 1, 1, 0], 0, 1, 0.1, 1, 3, 4, 1)
        with self.assertRaises(rt.ContractError):
            rt.trace_window([0, 1, 1], [0, 1, 2], 0, 1, 2, 1)

    def test_opamp_slew_and_supervisor_threshold_metrics(self):
        # Known synthetic traces exercise definitions, not real-device fidelity.
        time, output = rt.trace_window([0, 1, 2], [0, 2, 4], 0, 2, 3, 1)
        slew = (output[-1] - output[0]) / (time[-1] - time[0])
        self.assertEqual(slew, 2)
        rising = rt.crossing([0, 1, 2], [0, 0, 1], 0.5, "rising", 0, 2, 3, 1)
        falling = rt.crossing([0, 1, 2], [1, 0, 0], 0.5, "falling", 0, 2, 3, 1)
        self.assertEqual(rising - falling, 1)


class SuiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="spice harness spaces ")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / "suite"
        self.m = make_suite(self.root)

    def test_seal_validate_and_tamper(self):
        sha = rt.seal_suite(self.root)
        self.assertEqual(sha, rt.digest(self.root / "manifest.json"))
        m = rt.load_json(self.root / "manifest.json")
        rt.validate_manifest(m, self.root)
        with self.assertRaises(rt.ContractError):
            rt.seal_suite(self.root)
        (self.root / "extra.txt").write_text("unexpected", encoding="utf-8")
        with self.assertRaises(rt.ContractError):
            rt.validate_manifest(m, self.root)

    def test_changed_bench_hash(self):
        rt.seal_suite(self.root)
        (self.root / "benches" / "test.py").write_text("changed", encoding="utf-8")
        with self.assertRaises(rt.ContractError):
            rt.validate_manifest(rt.load_json(self.root / "manifest.json"), self.root)

    def test_unsupported_schema_family_and_joins(self):
        for key, value in (("schema_version", "2"), ("family", "transistor")):
            m = copy.deepcopy(self.m)
            m[key] = value
            with self.assertRaises(rt.ContractError):
                rt.validate_manifest(m, self.root, False)
        for change in (lambda m: m["tests"][0].update(requirement_ids=["unknown"]),
                       lambda m: m.update(coverage=[]),
                       lambda m: m["tests"][0].update(acceptance_role="advisory"),
                       lambda m: m["tests"][0].update(prerequisites=["unresolved"]),
                       lambda m: m["tests"][0].update(criterion=None),
                       lambda m: m["tests"][0].update(simulation_status="pass")):
            m = copy.deepcopy(self.m)
            change(m)
            with self.assertRaises(rt.ContractError):
                rt.validate_manifest(m, self.root, False)

    def test_partial_suite_keeps_gate(self):
        t = self.m["tests"][0]
        t.update(readiness="blocked", prerequisites=["approved accuracy budget"], criterion=None, bench=None)
        self.m["coverage"][0]["disposition"] = "blocked"
        rt.validate_manifest(self.m, self.root, False)
        self.assertEqual(rt.aggregate(self.m["tests"], [], self.m["coverage"]), "unresolved")

    def test_typical_values_cannot_claim_source_bounds(self):
        t = self.m["tests"][0]
        t["evidence_role"] = "target"
        t["criterion"].update(basis="source_limits", evidence_class="guaranteed")
        with self.assertRaises(rt.ContractError):
            rt.validate_manifest(self.m, self.root, False)

    def test_family_analysis_contracts(self):
        for family, analysis in (("operational_amplifier", "dc"), ("operational_amplifier", "ac"),
                                 ("operational_amplifier", "tran"), ("voltage_supervisor", "dc"),
                                 ("voltage_supervisor", "tran")):
            with self.subTest(family=family, analysis=analysis):
                root = self.parent / (family + analysis)
                m = make_suite(root, family, analysis)
                rt.validate_manifest(m, root, False)

    def test_exported_worker_and_wrapper_portability(self):
        model = self.parent / "model with spaces.sub"
        model.write_text(".SUBCKT DUT IN OUT\nE1 OUT 0 IN 0 1\n.ENDS DUT\n", encoding="utf-8")
        rt.model_contract(model, rt.load_json(self.root / "interface.json"))
        rt.seal_suite(self.root)
        run = self.parent / "worker"
        run.mkdir()
        for stage in ("build", "measure"):
            result = subprocess.run([sys.executable, "-B", str(self.root / "runtime.py"), "_worker", "--suite", str(self.root),
                                     "--test", "test_core", "--model", str(model), "--run-dir", str(run), "--stage", stage],
                                    cwd=self.parent, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, "-B", str(self.root / "run_suite.py"), "validate", "--suite", str(self.root)],
                                cwd=self.parent, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        rt.validate_manifest(rt.load_json(self.root / "manifest.json"), self.root)
        self.assertEqual(rt.load_json(run / "measurement.json")["value"], 1)

    def test_model_signature_and_includes(self):
        path = self.parent / "model.sub"
        interface = rt.load_json(self.root / "interface.json")
        for data in (".SUBCKT DUT OUT IN\n.ENDS DUT", ".include other.sub\n.SUBCKT DUT IN OUT\n.ENDS DUT"):
            path.write_text(data, encoding="utf-8")
            with self.assertRaises(rt.ContractError):
                rt.model_contract(path, interface)

    def test_results_cannot_be_written_inside_suite(self):
        rt.seal_suite(self.root)
        with self.assertRaises(rt.ContractError):
            rt.run_suite(self.root, self.parent / "absent.sub", result_parent=self.root / "runs")

    def test_missing_dependencies_global_blockers_and_repeated_runs(self):
        self.m["blockers"] = ["synthetic global approval needed"]
        (self.root / "manifest.json").write_text(json.dumps(self.m), encoding="utf-8")
        rt.seal_suite(self.root)
        first, report = rt.run_suite(self.root, self.parent / "missing.sub", ngspice="missing-simulator-fixture")
        second, _ = rt.run_suite(self.root, self.parent / "missing.sub", ngspice="missing-simulator-fixture")
        self.assertNotEqual(first, second)
        self.assertEqual(report["acceptance"], "unresolved")
        self.assertIn("synthetic global approval needed", report["preflight_blockers"])
        self.assertEqual(report["results"][0]["status"], "blocked")

    def test_mock_simulator_orchestration_is_not_device_validation(self):
        model = self.parent / "model.sub"
        model.write_text(".SUBCKT DUT IN OUT\nE1 OUT 0 IN 0 1\n.ENDS DUT\n", encoding="utf-8")
        rt.seal_suite(self.root)
        actual_run = rt.run_process

        def fake_simulator(argv, cwd, timeout_s, log_path):
            if argv[0] == "fake-ngspice":
                Path(log_path).write_text("MOCK SIMULATOR - NO DEVICE VALIDATION", encoding="utf-8")
                return {"status": "pass", "returncode": 0}
            return actual_run(argv, cwd, timeout_s, log_path)

        with patch.object(rt, "run_process", side_effect=fake_simulator), patch.object(rt.importlib.metadata, "version", return_value="mock"):
            _, report = rt.run_suite(self.root, model, "fake-ngspice")
        self.assertEqual(report["acceptance"], "accepted")
        self.assertEqual(report["results"][0]["status"], "pass")

    def test_dut_deck_without_model_is_rejected(self):
        bench = self.root / "benches" / "test.py"
        bench.write_text("def build_deck(model_path, interface, test):\n    return 'Divider only\\n.end'\n", encoding="utf-8")
        run = self.parent / "worker"
        run.mkdir()
        with self.assertRaises(rt.ContractError):
            rt.worker(self.root, "test_core", self.parent / "model.sub", run, "build")

    def test_aggregation(self):
        tests = self.m["tests"]
        for status in ("not_run", "error", "timeout", "blocked"):
            self.assertEqual(rt.aggregate(tests, [{"test_id": "test_core", "status": status}]), "unresolved")
        self.assertEqual(rt.aggregate(tests, [{"test_id": "test_core", "status": "fail"}]), "rejected")
        self.assertEqual(rt.aggregate(tests, [{"test_id": "test_core", "status": "pass"}]), "accepted")
        advisory = copy.deepcopy(tests[0])
        advisory.update(id="advisory", acceptance_role="advisory")
        self.assertEqual(rt.aggregate(tests + [advisory], [{"test_id": "test_core", "status": "pass"},
                                                       {"test_id": "advisory", "status": "fail"}]), "accepted")
        self.assertEqual(rt.aggregate([], []), "unresolved")

    def test_paths_and_strict_json(self):
        for path in ("../escape", "benches/CON.py", "NUL", "benches/name. ", "C:/escape", "benches\\x.py", "a//b"):
            with self.subTest(path=path), self.assertRaises(rt.ContractError):
                rt.safe_path(self.root, path)
        path = self.parent / "invalid.json"
        for content in ('{"x": NaN}', '{"x":1,"x":2}'):
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(rt.ContractError):
                rt.load_json(path)

    def test_synthetic_template_refuses_dut(self):
        spec = importlib.util.spec_from_file_location("fixture_template", SCRIPTS.parent / "templates" / "bench.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaises(ValueError):
            module.build_deck(self.parent / "model", {}, self.m["tests"][0])


class ProcessTests(unittest.TestCase):
    def test_pass_fail_timeout(self):
        with tempfile.TemporaryDirectory(prefix="process harness ") as temporary:
            root = Path(temporary)
            cases = [("pass", "print('known result')", 5), ("error", "raise ValueError('malformed fixture')", 5),
                     ("timeout", "import time; time.sleep(30)", 0.2)]
            for expected, script, timeout in cases:
                with self.subTest(expected=expected):
                    result = rt.run_process([sys.executable, "-c", script], root, timeout, root / f"{expected}.log")
                    self.assertEqual(result["status"], expected, result)
                    self.assertTrue((root / f"{expected}.log").is_file())

    def test_normal_exit_kills_descendant(self):
        with tempfile.TemporaryDirectory(prefix="child ownership ") as temporary:
            root = Path(temporary)
            # The descendant would create this marker if left running after its parent exits.
            child = "import time; from pathlib import Path; time.sleep(1); Path('orphan.txt').write_text('orphan')"
            script = f"import subprocess,sys; subprocess.Popen([sys.executable,'-c',{child!r}])"
            result = rt.run_process([sys.executable, "-c", script], root, 5, root / "tree.log")
            self.assertEqual(result["status"], "pass", result)
            time.sleep(1.2)
            self.assertFalse((root / "orphan.txt").exists(), "Descendant escaped process ownership")


class AuthoringArtifactTests(unittest.TestCase):
    def test_thin_agent_command_and_canonical_layout(self):
        repository = SCRIPTS.parents[2]
        agent = (repository / ".mplab-ai" / "agent" / "test-author.md").read_text(encoding="utf-8")
        command = (repository / ".mplab-ai" / "command" / "test-author.md").read_text(encoding="utf-8")
        skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("mode: subagent", agent)
        self.assertIn("skills/test-author/SKILL.md", agent)
        self.assertIn("agent: test-author", command)
        self.assertIn("subtask: true", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("name: test-author", skill)
        self.assertNotIn("C:\\Users\\", agent + command + skill)

    @unittest.skipUnless(importlib.util.find_spec("PySpice"), "PySpice unavailable")
    def test_pyspice_constructs_synthetic_batch_deck_without_dll(self):
        spec = importlib.util.spec_from_file_location("fixture_template", SCRIPTS.parent / "templates" / "bench.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        deck = module.build_deck(Path("unused"), {}, {"purpose": "harness_fixture"})
        self.assertIn("wrdata trace.txt v(output)", deck)
        self.assertIn("Rupper", deck)
        self.assertIn(".control", deck)


@unittest.skipUnless(shutil.which("ngspice") and importlib.util.find_spec("PySpice"), "ngspice/PySpice unavailable")
class SimulatorSmokeTests(unittest.TestCase):
    def test_real_divider_harness_only(self):
        spec = importlib.util.spec_from_file_location("fixture_template", SCRIPTS.parent / "templates" / "bench.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix="ngspice fixture ") as temporary:
            root = Path(temporary)
            (root / "deck.cir").write_text(module.build_deck(Path("unused"), {}, {"purpose": "harness_fixture"}), encoding="utf-8")
            result = rt.run_process([shutil.which("ngspice"), "-n", "-b", "deck.cir"], root, 10, root / "simulator.log")
            self.assertEqual(result["status"], "pass")
            value = module.measure(root, {})
            self.assertEqual(rt.evaluate(value, criterion(min=0.99, max=1.01))["status"], "pass")
            self.assertEqual(rt.evaluate(value, criterion(min=2, max=3))["status"], "fail")
            (root / "bad.cir").write_text("Malformed fixture\nRbad no_nodes\n.end\n", encoding="utf-8")
            result = rt.run_process([shutil.which("ngspice"), "-n", "-b", "bad.cir"], root, 10, root / "malformed.log")
            self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()
