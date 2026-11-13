"""SYNTHETIC API EXAMPLE ONLY: replace with a source-supported device bench.

The divider validates batch plumbing; it is not an op-amp/supervisor model.
Run only as a labeled fixture, never as a DUT acceptance test.
"""

from pathlib import Path


def build_deck(model_path: Path, interface: dict, test: dict) -> str:
    if test.get("purpose") != "harness_fixture":
        raise ValueError("Synthetic divider refuses DUT acceptance execution; author a real device bench")
    from PySpice.Spice.Netlist import Circuit

    circuit = Circuit("Synthetic divider harness fixture - not a DUT")
    circuit.V("supply", "supply", circuit.gnd, 2)
    circuit.R("upper", "supply", "output", 1000)
    circuit.R("lower", "output", circuit.gnd, 1000)
    # Real benches include the self-contained model and connect the accepted
    # ordered terminals. Numerical conditions come from test, not guessed defaults.
    return str(circuit) + """
.control
set wr_singlescale
set wr_vecnames
op
wrdata trace.txt v(output)
quit
.endc
.end
"""


def measure(run_dir: Path, test: dict) -> dict:
    lines = (run_dir / "trace.txt").read_text(encoding="utf-8").splitlines()
    rows = []
    for line in lines:
        try:
            rows.append([float(v) for v in line.split()])
        except ValueError:
            continue  # The example ngspice export has one text header.
    if len(rows) != 1 or len(rows[0]) != 2:
        raise ValueError("Expected one operating-point row with scale and output columns")
    return {"value": rows[0][1], "unit": "V"}
