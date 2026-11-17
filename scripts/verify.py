"""Run real checks and preserve timestamped, machine-readable development evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc)
    commands = [
        [sys.executable, "-m", "pip", "check"],
        [sys.executable, "-m", "pytest", "-q", "--cov=career_intelligence", "--cov=app",
         "--cov-report=term-missing", f"--cov-report=json:{output / 'coverage.json'}",
         f"--junitxml={output / 'junit.xml'}"],
    ]
    results = []
    for name, command in zip(["dependency-check", "pytest"], commands):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        (output / f"{name}.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        results.append({"check": name, "command": command, "exit_code": result.returncode})
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    versions = {}
    for package in ["pandas", "numpy", "streamlit", "plotly", "pytest", "pytest-cov"]:
        versions[package] = importlib.metadata.version(package)
    manifest = {}
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in {".git", ".venv", "__pycache__", ".pytest_cache", "evidence"} for part in relative.parts):
            continue
        if path.is_file() and (path.suffix in {".py", ".csv", ".toml", ".txt", ".yml"}) and path.name != "package.json":
            manifest[str(relative).replace("\\", "/")] = hashlib.sha256(path.read_bytes()).hexdigest()
    suites = ET.parse(output / "junit.xml").getroot().findall("testsuite") if (output / "junit.xml").exists() else []
    counts = {key: sum(int(suite.get(key, 0)) for suite in suites) for key in ["tests", "failures", "errors", "skipped"]}
    record = {
        "started_at_utc": started.isoformat(), "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution": "Automated assistant build environment; not student practicum hours",
        "python": sys.version, "platform": platform.platform(), "packages": versions,
        "checks": results, "test_counts": counts, "sha256": manifest,
    }
    (output / "verification.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence saved: {output}")
    return int(any(check["exit_code"] != 0 for check in results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / "evidence" / "local-runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    raise SystemExit(run(output.resolve()))
