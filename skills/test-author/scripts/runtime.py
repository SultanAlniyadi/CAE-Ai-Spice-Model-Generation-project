"""Portable acceptance-suite validation and isolated ngspice execution (Python 3.10+)."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time


class ContractError(ValueError):
    """An incomplete, contradictory or changed acceptance contract."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest() if sys.version_info >= (3, 11) else _digest(stream)


def _digest(stream):
    sha = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        sha.update(chunk)
    return sha.hexdigest()


def load_json(path):
    def reject(value):
        raise ContractError(f"Nonfinite JSON constant: {value}")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream, parse_constant=reject, object_pairs_hook=unique)


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def safe_path(root, relative):
    require(isinstance(relative, str) and relative and "\\" not in relative,
            f"Use nonempty portable slash-separated paths: {relative!r}")
    require(not re.search(r"[:\x00-\x1f]", relative), f"Unsafe path: {relative}")
    path = Path(relative)
    require(all(portable_name(part) for part in relative.split("/")), f"Nonportable path: {relative}")
    require(not path.is_absolute() and all(p not in (".", "..") for p in relative.split("/"))
            and "" not in relative.split("/"), f"Unsafe path: {relative}")
    root = Path(root).resolve()
    result = root.joinpath(path)
    require(result.resolve().is_relative_to(root), f"Path escapes suite: {relative}")
    require(not any(p.is_symlink() for p in [result, *result.parents] if p != root and p.is_relative_to(root)),
            f"Symlink in suite: {relative}")
    return result


def portable_name(name):
    return bool(name) and not name.endswith((".", " ")) and not re.fullmatch(
        r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", name)


def inventory(root):
    root = Path(root).resolve()
    result = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), f"Symlink in suite: {path}")
        if path.is_file() and path.name != "manifest.json":
            name = path.relative_to(root).as_posix()
            safe_path(root, name)
            result[name] = digest(path)
        elif path.is_file():
            require(path == root / "manifest.json", "Nested manifest.json is not allowed")
    require(len({name.casefold() for name in result}) == len(result), "Case-colliding suite paths")
    return result


def fields(obj, names, label):
    require(isinstance(obj, dict), f"{label} must be an object")
    require(set(names) <= obj.keys(), f"{label} missing fields: {set(names) - obj.keys()}")


def text(value, label):
    require(isinstance(value, str) and value.strip(), f"{label} must be nonempty text")


def approval(obj):
    fields(obj, ("by", "reference"), "approval")
    text(obj["by"], "approval.by")
    text(obj["reference"], "approval.reference")


def source_refs(refs, sources):
    require(isinstance(refs, list) and refs, "Source provenance is required")
    for ref in refs:
        fields(ref, ("source_id", "locator"), "source reference")
        require(ref["source_id"] in sources, f"Unknown source: {ref['source_id']}")
        text(ref["locator"], "source locator")
        for key in ("entity_ids", "condition_group_ids", "circuit_ids", "quality_ids"):
            if key in ref:
                require(isinstance(ref[key], list) and all(isinstance(v, str) and v for v in ref[key]),
                        f"Invalid {key}")


def validate_criterion(c):
    fields(c, ("kind", "unit", "basis", "provenance"), "criterion")
    text(c["unit"], "criterion.unit")
    require(c["basis"] in ("source_limits", "approved_budget"), "Unknown criterion basis")
    if c["basis"] == "approved_budget":
        approval(c.get("approval"))
    else:
        require(c.get("evidence_class") in ("guaranteed", "specified_functional"),
                "Source bounds require guaranteed/specified-functional evidence")
    kind = c["kind"]
    require(kind in ("interval", "minimum", "maximum", "absolute_error", "relative_error", "curve_error"),
            f"Unsupported criterion: {kind}")
    for key in (("min", "max") if kind == "interval" else
                ("min",) if kind == "minimum" else ("max",) if kind == "maximum" else ("tolerance",)):
        require(number(c.get(key)), f"criterion.{key} must be finite")
    if kind == "interval":
        require(c["min"] <= c["max"], "Reversed interval")
    if kind in ("absolute_error", "relative_error", "curve_error"):
        require(c["tolerance"] >= 0, "Negative tolerance")
        if kind == "curve_error":
            require(isinstance(c.get("reference"), list) and c["reference"]
                    and all(number(v) for v in c["reference"]), "Invalid reference curve")
            require(c.get("reduction") in ("max", "rms"), "Unknown curve reduction")
            if c.get("period") is not None:
                require(number(c["period"]) and c["period"] > 0, "Invalid wrapping period")
        else:
            require(number(c.get("reference")), "Invalid scalar reference")
        if kind == "relative_error":
            require(number(c.get("zero_floor")) and c["zero_floor"] > 0, "Positive zero_floor required")


def validate_manifest(m, root, verify_hashes=True):
    fields(m, ("schema_version", "suite_id", "suite_version", "family", "target", "sources",
               "interface_file", "simulator", "requirements", "coverage", "tests", "hashes",
               "assumptions", "blockers", "harness_validation"), "manifest")
    require(m["schema_version"] == "1.0.0", "Unsupported suite schema")
    require(m["family"] in ("operational_amplifier", "voltage_supervisor"), "Unsupported family")
    text(m["suite_id"], "suite_id")
    text(m["suite_version"], "suite_version")
    fields(m["target"], ("part", "variant", "package", "grade", "channel", "scope"), "target")
    text(m["target"]["part"], "target.part")
    text(m["target"]["scope"], "target.scope")
    for key in ("assumptions", "blockers", "sources", "requirements", "coverage", "tests"):
        require(isinstance(m[key], list), f"{key} must be a list")
    require(m["sources"] and m["requirements"] and m["tests"], "Empty evidence/requirements/tests")
    sources = {}
    for s in m["sources"]:
        fields(s, ("id", "kind", "sha256", "revision", "locator"), "source")
        text(s["id"], "source.id")
        require(s["id"] not in sources, "Duplicate source ID")
        require(isinstance(s["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", s["sha256"]), "Invalid source hash")
        text(s["kind"], "source.kind")
        text(s["locator"], "source.locator")
        sources[s["id"]] = s
    sim = m["simulator"]
    fields(sim, ("backend", "required_features", "timeout_s"), "simulator")
    require(sim["backend"] == "ngspice_batch", "Only isolated ngspice batch is supported")
    require(isinstance(sim["required_features"], list), "required_features must be a list")
    require(number(sim["timeout_s"]) and sim["timeout_s"] > 0, "Invalid simulator timeout")
    interface = load_json(safe_path(root, m["interface_file"]))
    fields(interface, ("subcircuit", "terminals", "status", "source_refs"), "interface")
    require(isinstance(interface["subcircuit"], str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", interface["subcircuit"]),
            "Unsafe subcircuit name")
    require(interface["status"] in ("proposed", "accepted"), "Invalid interface status")
    if interface["status"] == "accepted":
        approval(interface.get("approval"))
    source_refs(interface["source_refs"], sources)
    require(isinstance(interface["terminals"], list) and interface["terminals"], "No interface terminals")
    terminal_names = []
    for terminal in interface["terminals"]:
        fields(terminal, ("name", "role", "pin_ids", "channel"), "terminal")
        require(isinstance(terminal["name"], str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", terminal["name"]),
                "Unsafe terminal name")
        text(terminal["role"], "terminal.role")
        require(isinstance(terminal["pin_ids"], list) and terminal["pin_ids"], "Terminal lacks pin evidence")
        terminal_names.append(terminal["name"].casefold())
    require(len(terminal_names) == len(set(terminal_names)), "Duplicate terminals")
    requirements = {}
    for r in m["requirements"]:
        fields(r, ("id", "description", "source_refs", "mandatory", "core"), "requirement")
        text(r["id"], "requirement.id")
        require(r["id"] not in requirements, "Duplicate requirement ID")
        text(r["description"], "requirement.description")
        require(type(r["mandatory"]) is bool and type(r["core"]) is bool, "Requirement flags must be booleans")
        source_refs(r["source_refs"], sources)
        requirements[r["id"]] = r
    tests = {}
    for t in m["tests"]:
        fields(t, ("id", "requirement_ids", "description", "behavior", "applicability", "priority",
                   "acceptance_role", "role_reason", "readiness", "prerequisites", "analysis",
                   "conditions", "stimulus", "fixture", "metric", "criterion", "source_refs",
                   "reference_files", "evidence_role", "bench", "timeout_s", "simulation_status"), "test")
        require(isinstance(t["id"], str) and re.fullmatch(r"[A-Za-z0-9_-]+", t["id"]), "Unsafe test ID")
        require(portable_name(t["id"]), "Reserved test ID")
        require(t["id"].casefold() not in {v.casefold() for v in tests}, "Duplicate test ID")
        require(isinstance(t["requirement_ids"], list) and t["requirement_ids"]
                and all(v in requirements for v in t["requirement_ids"]), "Broken test requirement join")
        for key in ("description", "behavior", "applicability", "role_reason"):
            text(t[key], f"test.{key}")
        require(t["priority"] in ("critical", "high", "medium", "low"), "Invalid priority")
        require(t["acceptance_role"] in ("blocking", "advisory"), "Invalid acceptance role")
        require(t["readiness"] in ("ready", "blocked", "out_of_scope"), "Invalid readiness")
        require(t["simulation_status"] == "not_run", "DUT results cannot be stored in suite")
        require(t["analysis"] in ("op", "dc", "ac", "tran", "noise"), "Invalid analysis")
        require(t["evidence_role"] in ("fitting", "holdout", "functional", "target"), "Invalid evidence role")
        require(isinstance(t["prerequisites"], list), "Invalid prerequisites")
        require(number(t["timeout_s"]) and t["timeout_s"] > 0, "Invalid test timeout")
        source_refs(t["source_refs"], sources)
        require(isinstance(t["reference_files"], list), "reference_files must be a list")
        for path in t["reference_files"]:
            require(safe_path(root, path).is_file(), f"Missing reference: {path}")
        if t["criterion"] is not None:
            validate_criterion(t["criterion"])
            source_refs(t["criterion"]["provenance"], sources)
            require(not (t["evidence_role"] == "target" and t["criterion"]["basis"] == "source_limits"),
                    "Typical targets require approved budgets")
        if t["readiness"] == "ready":
            require(not t["prerequisites"], "Ready test has unresolved prerequisites")
            for key in ("conditions", "stimulus", "fixture"):
                require(isinstance(t[key], dict) and t[key], f"Ready test lacks {key}")
            fields(t["metric"], ("name", "unit", "definition", "window", "resolution"), "metric")
            for key in ("name", "unit", "definition"):
                text(t["metric"][key], f"metric.{key}")
            require(t["metric"]["window"] and t["metric"]["resolution"], "Incomplete measurement window/resolution")
            require(t["criterion"] is not None and t["criterion"]["unit"] == t["metric"]["unit"],
                    "Ready test lacks compatible criterion")
            require(isinstance(t["bench"], str) and t["bench"].startswith("benches/")
                    and t["bench"].endswith(".py") and safe_path(root, t["bench"]).is_file(), "Missing bench")
        else:
            require(t["prerequisites"] or t["readiness"] == "out_of_scope", "Blocked test lacks explanation")
        tests[t["id"]] = t
    covered = set()
    for c in m["coverage"]:
        fields(c, ("requirement_id", "test_ids", "disposition", "reason"), "coverage")
        rid = c["requirement_id"]
        require(rid in requirements and rid not in covered, "Missing/duplicate coverage requirement")
        covered.add(rid)
        require(c["disposition"] in ("covered", "blocked", "out_of_scope"), "Invalid coverage disposition")
        text(c["reason"], "coverage.reason")
        require(isinstance(c["test_ids"], list) and all(t in tests and rid in tests[t]["requirement_ids"]
                                                     for t in c["test_ids"]), "Broken coverage join")
        related = [tests[t] for t in c["test_ids"]]
        if c["disposition"] == "out_of_scope":
            approval(c.get("scope_approval"))
            require(all(t["readiness"] == "out_of_scope" for t in related), "Excluded coverage has in-scope tests")
        else:
            require(related, "In-scope requirement has no test record")
            require(all(t["readiness"] != "out_of_scope" for t in related), "In-scope coverage excludes tests")
            require(c["disposition"] != "covered" or all(t["readiness"] == "ready" for t in related),
                    "Covered obligation contains blocked tests")
            if requirements[rid]["core"] or requirements[rid]["mandatory"]:
                require(any(t["acceptance_role"] == "blocking" for t in related), "Mandatory/core coverage lacks gate")
    require(covered == set(requirements), "Incomplete coverage ledger")
    for t in tests.values():
        require(all(any(c["requirement_id"] == r and t["id"] in c["test_ids"] for c in m["coverage"])
                    for r in t["requirement_ids"]), "Test is omitted from coverage")
    fields(m["harness_validation"], ("status", "evidence_files"), "harness_validation")
    require(m["harness_validation"]["status"] in ("not_run", "pass", "fail", "blocked"), "Invalid harness status")
    require(isinstance(m["harness_validation"]["evidence_files"], list), "Invalid harness evidence list")
    require(m["harness_validation"]["status"] != "pass" or m["harness_validation"]["evidence_files"],
            "Harness pass requires evidence")
    for path in m["harness_validation"]["evidence_files"]:
        require(safe_path(root, path).is_file(), "Missing harness evidence")
    require(isinstance(m["hashes"], dict), "hashes must be an object")
    if verify_hashes:
        require(m["hashes"] == inventory(root), "Suite inventory/hash mismatch; do not reseal during fitting")
    return interface


def evaluate(measurement, criterion):
    validate_criterion(criterion)
    require(isinstance(measurement, dict) and measurement.get("valid", True) is True, "Invalid measurement")
    require(measurement.get("unit") == criterion["unit"], "Measurement unit mismatch")
    kind = criterion["kind"]
    if kind == "curve_error":
        values = measurement.get("values")
        refs = criterion["reference"]
        require(isinstance(values, list) and len(values) == len(refs) and all(number(v) for v in values),
                "Missing/nonfinite/misaligned curve samples")
        errors = [v - r for v, r in zip(values, refs)]
        period = criterion.get("period")
        if period:
            errors = [(e + period / 2) % period - period / 2 for e in errors]
        error = max(abs(e) for e in errors) if criterion["reduction"] == "max" else math.hypot(*errors) / math.sqrt(len(errors))
        passed = error <= criterion["tolerance"]
        value = error
    else:
        value = measurement.get("value")
        require(number(value), "Missing/nonfinite scalar measurement or absent event")
        error = None
        if kind == "interval":
            passed = criterion["min"] <= value <= criterion["max"]
        elif kind == "minimum":
            passed = value >= criterion["min"]
        elif kind == "maximum":
            passed = value <= criterion["max"]
        else:
            error = abs(value - criterion["reference"])
            if kind == "relative_error":
                error /= max(abs(criterion["reference"]), criterion["zero_floor"])
            passed = error <= criterion["tolerance"]
    require(number(value) and (error is None or number(error)), "Overflow in metric computation")
    return {"status": "pass" if passed else "fail", "value": value, "error": error, "unit": criterion["unit"]}


def trace_window(x, y, start, end, min_samples, max_step):
    """Validate a single connected, increasing trace segment and select its window.

    Never use across evidence gaps or repeated-X branches. Units and coordinates
    must already match the manifest; no extrapolation or implicit resampling.
    """
    require(isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and len(x) >= 2,
            "Missing/misaligned trace")
    require(all(number(v) for v in x + y), "Nonfinite trace")
    require(all(b > a for a, b in zip(x, x[1:])), "Trace must be one increasing connected segment")
    require(number(start) and number(end) and start < end, "Invalid window")
    require(x[0] <= start and x[-1] >= end, "Insufficient observation window")
    require(type(min_samples) is int and min_samples >= 2 and number(max_step) and max_step > 0,
            "Explicit positive resolution settings required")
    pairs = [(a, b) for a, b in zip(x, y) if start <= a <= end]
    require(len(pairs) >= min_samples, "Insufficient window samples")
    require(all(b - a <= max_step for a, b in zip(x, x[1:]) if b >= start and a <= end),
            "Trace exceeds maximum timestep/sweep spacing")
    return [p[0] for p in pairs], [p[1] for p in pairs]


def crossing(x, y, level, direction, start, end, min_samples, max_step):
    """Unique directional crossing using explicitly linear interpolation."""
    xx, yy = trace_window(x, y, start, end, min_samples, max_step)
    require(number(level) and direction in ("rising", "falling"), "Invalid crossing definition")
    events = []
    for a, b, va, vb in zip(xx, xx[1:], yy, yy[1:]):
        crossed = va < level <= vb if direction == "rising" else va > level >= vb
        if crossed:
            events.append(a + (level - va) * (b - a) / (vb - va))
    require(len(events) == 1, "Expected one qualified crossing; absent/ambiguous event")
    return events[0]


def settling_time(x, y, event, final, band, dwell, end, min_samples, max_step):
    """First sampled final band entry sustained through the observation end.

    This sampled estimator does not interpolate entry; max_step constrains its
    uncertainty. Final reference must come from the acceptance definition.
    """
    require(number(final) and number(band) and band >= 0 and number(dwell) and dwell > 0,
            "Invalid settling reference/band/dwell")
    xx, yy = trace_window(x, y, event, end, min_samples, max_step)
    last_out = max((i for i, value in enumerate(yy) if abs(value - final) > band), default=-1)
    first = last_out + 1
    require(first < len(xx) and end - xx[first] >= dwell, "No final entry with sufficient settling dwell")
    return xx[first] - event


def aggregate(tests, results, coverage=None):
    statuses = {r["test_id"]: r["status"] for r in results}
    gates = [t for t in tests if t["acceptance_role"] == "blocking" and t["readiness"] != "out_of_scope"]
    if any(statuses.get(t["id"]) == "fail" for t in gates):
        return "rejected"
    if not gates or any(statuses.get(t["id"], "not_run") != "pass" for t in gates):
        return "unresolved"
    if coverage is not None and any(c["disposition"] == "blocked" for c in coverage):
        return "unresolved"
    return "accepted"


def run_process(argv, cwd, timeout_s, log_path):
    require(number(timeout_s) and timeout_s > 0, "Finite positive process timeout required")
    log_path = Path(log_path)
    job = None
    with log_path.open("x", encoding="utf-8") as log:
        try:
            process = subprocess.Popen(argv, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=os.name != "nt",
                                       creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP | 0x4) if os.name == "nt" else 0)
        except OSError as exc:
            log.write(str(exc))
            return {"status": "error", "detail": str(exc), "returncode": None}
        if os.name == "nt":
            try:
                job = WindowsJob(process)
                # Assign while suspended so a fast bench cannot spawn unowned children.
                import ctypes
                from ctypes import wintypes
                resume = ctypes.WinDLL("ntdll").NtResumeProcess
                resume.argtypes = [wintypes.HANDLE]
                resume.restype = ctypes.c_long
                if resume(wintypes.HANDLE(int(process._handle))) != 0:
                    raise OSError("Failed to resume job-owned process")
            except OSError as exc:
                if job:
                    job.close()
                process.kill()
                process.wait(timeout=10)
                return {"status": "error", "detail": f"Cannot own child process tree: {exc}", "returncode": process.returncode}
        try:
            code = process.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            cleanup_process_tree(process, job)
            job = None
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            return {"status": "timeout", "returncode": process.returncode}
        finally:
            cleanup_process_tree(process, job)
    return {"status": "pass" if code == 0 else "error", "returncode": code}


class WindowsJob:
    """Own descendants with a kill-on-close Job Object, including normal parent exit."""

    def __init__(self, process):
        import ctypes
        from ctypes import wintypes

        class Basic(ctypes.Structure):
            _fields_ = [("ProcessTime", ctypes.c_int64), ("JobTime", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinWorking", ctypes.c_size_t),
                        ("MaxWorking", ctypes.c_size_t), ("ActiveLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("Priority", wintypes.DWORD), ("Scheduling", wintypes.DWORD)]

        class Io(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ("ReadOps", "WriteOps", "OtherOps", "ReadBytes", "WriteBytes", "OtherBytes")]

        class Extended(ctypes.Structure):
            _fields_ = [("Basic", Basic), ("Io", Io), ("ProcessMemory", ctypes.c_size_t),
                        ("JobMemory", ctypes.c_size_t), ("PeakProcess", ctypes.c_size_t), ("PeakJob", ctypes.c_size_t)]

        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        info = Extended()
        info.Basic.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)) or not self.kernel.AssignProcessToJobObject(self.handle, wintypes.HANDLE(int(process._handle))):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def close(self):
        if self.handle:
            if not self.kernel.CloseHandle(self.handle):
                raise OSError("Failed to close process-tree Job Object")
            self.handle = None


def cleanup_process_tree(process, job):
    if job:
        job.close()
    elif os.name != "nt":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def model_contract(model, interface):
    data = Path(model).read_text(encoding="utf-8")
    require(not re.search(r"(?im)^\s*\.(include|inc|lib)\b", data),
            "Supply a self-contained model; external model includes are unsupported")
    data = re.sub(r"\r?\n\s*\+", " ", data)
    matches = re.findall(r"(?im)^\s*\.subckt\s+([^\s]+)\s+([^\r\n]+)", data)
    matching = [nodes for name, nodes in matches if name.casefold() == interface["subcircuit"].casefold()]
    require(len(matching) == 1, "Expected exactly one matching .SUBCKT")
    nodes = re.split(r"(?i)\s+params:|\s+\w+=", matching[0])[0].split()
    require([n.casefold() for n in nodes] == [t["name"].casefold() for t in interface["terminals"]],
            "Model terminal order does not match accepted interface")


def import_bench(path):
    # Authored benches are trusted code, not sandboxed. Never write bytecode in a frozen suite.
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("suite_bench", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous


def worker(root, test_id, model, run_dir, stage):
    root, run_dir = Path(root).resolve(), Path(run_dir).resolve()
    m = load_json(root / "manifest.json")
    t = next(t for t in m["tests"] if t["id"] == test_id)
    interface = load_json(root / m["interface_file"])
    module = import_bench(safe_path(root, t["bench"]))
    if stage == "build":
        deck = module.build_deck(Path(model), interface, t)
        require(isinstance(deck, str) and deck.strip(), "Bench returned no deck")
        model_text = str(Path(model).resolve())
        require(model_text in deck, "DUT deck does not include the supplied model path")
        require(re.search(r"(?im)^\s*x\S*\s+[^\r\n]*\b" + re.escape(interface["subcircuit"]) + r"(?:\s|$)", deck),
                "DUT deck does not instantiate the accepted subcircuit")
        with (run_dir / "deck.cir").open("x", encoding="utf-8") as stream:
            stream.write(deck)
    else:
        measurement = module.measure(run_dir, t)
        write_json(run_dir / "measurement.json", measurement)


def run_suite(root, model_path, ngspice="ngspice", result_parent=None):
    root = Path(root).resolve()
    m = load_json(root / "manifest.json")
    interface = validate_manifest(m, root)
    manifest_hash = digest(root / "manifest.json")
    parent = Path(result_parent).resolve() if result_parent else root.parent / "runs"
    require(not parent.is_relative_to(root), "Results must live outside the immutable suite")
    parent.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    model = Path(model_path).resolve()
    blocked = list(m["blockers"])
    if "/" in str(ngspice) or "\\" in str(ngspice):
        ngspice = str(Path(ngspice).resolve())
    model_hash = None
    try:
        require(model.is_file(), "Model path is missing")
        require(not re.search(r'["\r\n]', str(model)), "Unsafe model include path")
        require(interface["status"] == "accepted", "Interface still requires parent approval")
        model_contract(model, interface)
        model_hash = digest(model)
    except (OSError, ContractError) as exc:
        blocked.append(str(exc))
    try:
        pyspice_version = importlib.metadata.version("PySpice")
    except importlib.metadata.PackageNotFoundError:
        pyspice_version = None
        blocked.append("PySpice is not installed; no automatic installation")
    version_check = run_process([ngspice, "--version"], run, 10, run / "ngspice-version.log")
    if version_check["status"] != "pass":
        blocked.append("ngspice executable/version preflight failed")
    if m["simulator"]["required_features"]:
        blocked.append("Optional simulator features require a reviewed runner extension/probe")
    results = []
    for t in m["tests"]:
        result = {"test_id": t["id"], "status": "not_run"}
        if t["readiness"] == "out_of_scope":
            result["detail"] = "Approved out-of-scope coverage"
        elif blocked or t["readiness"] == "blocked":
            result.update(status="blocked", detail=blocked + t["prerequisites"])
        else:
            test_dir = run / t["id"]
            test_dir.mkdir()
            timeout = t["timeout_s"]
            deadline = time.monotonic() + timeout
            stages = [
                ("build", [sys.executable, "-B", str(Path(__file__).resolve()), "_worker", "--suite", str(root),
                           "--test", t["id"], "--model", str(model), "--run-dir", str(test_dir), "--stage", "build"]),
                ("simulate", [ngspice, "-n", "-b", "-o", "ngspice.log", "deck.cir"]),
                ("measure", [sys.executable, "-B", str(Path(__file__).resolve()), "_worker", "--suite", str(root),
                             "--test", t["id"], "--model", str(model), "--run-dir", str(test_dir), "--stage", "measure"]),
            ]
            for stage, argv in stages:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    result.update(status="timeout", stage=stage)
                    break
                budget = min(remaining, m["simulator"]["timeout_s"]) if stage == "simulate" else remaining
                outcome = run_process(argv, test_dir, budget, test_dir / f"{stage}.log")
                if outcome["status"] != "pass":
                    result.update(outcome, stage=stage)
                    break
            else:
                try:
                    measurement = load_json(test_dir / "measurement.json")
                    result.update(evaluate(measurement, t["criterion"]), measurement=measurement)
                    if time.monotonic() > deadline:
                        result.update(status="timeout", detail="Test deadline exceeded during metric evaluation")
                except (OSError, ValueError, TypeError) as exc:
                    result.update(status="error", detail=str(exc))
        results.append(result)
    acceptance = aggregate(m["tests"], results, m["coverage"])
    integrity = []
    try:
        validate_manifest(load_json(root / "manifest.json"), root)
        require(digest(root / "manifest.json") == manifest_hash, "Manifest changed during execution")
        if model_hash:
            require(digest(model) == model_hash, "Model changed during execution")
    except (OSError, ValueError) as exc:
        integrity.append(str(exc))
        acceptance = "unresolved"
    report = {"schema_version": "1.0.0", "suite_id": m["suite_id"], "suite_version": m["suite_version"],
              "manifest_sha256": manifest_hash, "model_sha256": model_hash, "model": str(model),
              "python": sys.version, "pyspice": pyspice_version, "ngspice_version_log": "ngspice-version.log",
              "preflight_blockers": blocked, "integrity_errors": integrity, "results": results,
              "acceptance": acceptance}
    write_json(run / "results.json", report)
    return run, report


def seal_suite(root):
    root = Path(root).resolve()
    manifest = root / "manifest.json"
    m = load_json(manifest)
    validate_manifest(m, root, verify_hashes=False)
    require(not m["hashes"], "Already sealed: reauthor into a new version instead of resealing")
    m["hashes"] = inventory(root)
    temporary = root / ".manifest-sealing.tmp"
    try:
        write_json(temporary, m)
        temporary.replace(manifest)
    finally:
        if temporary.exists():
            temporary.unlink()
    validate_manifest(m, root)
    return digest(manifest)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "seal", "run", "_worker"))
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--ngspice", default="ngspice")
    parser.add_argument("--results", type=Path)
    parser.add_argument("--test")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--stage", choices=("build", "measure"))
    args = parser.parse_args(argv)
    try:
        if args.command == "_worker":
            worker(args.suite, args.test, args.model, args.run_dir, args.stage)
            return 0
        if args.command == "seal":
            print(json.dumps({"manifest_sha256": seal_suite(args.suite)}))
        elif args.command == "validate":
            validate_manifest(load_json(args.suite / "manifest.json"), args.suite)
            print(json.dumps({"status": "valid", "manifest_sha256": digest(args.suite / "manifest.json")}))
        else:
            require(args.model is not None, "run requires --model")
            path, report = run_suite(args.suite, args.model, args.ngspice, args.results)
            print(json.dumps({"results": str(path / "results.json"), "acceptance": report["acceptance"]}))
            return 0 if report["acceptance"] == "accepted" else 1
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "detail": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
