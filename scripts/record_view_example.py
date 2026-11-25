"""Record a reproducible filtered-view download and its extracted evidence."""

import argparse
import hashlib
import json
import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from career_intelligence.analytics import Filters, filter_jobs
from career_intelligence.data import load_csv
from career_intelligence.exports import export_view_bundle


def run(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / "tests/fixtures/analytics_cases.csv"
    raw = fixture.read_bytes()
    jobs = load_csv(raw).jobs
    filters = Filters(locations=("Seattle, WA",), work_modes=("Remote",))
    payload = export_view_bundle(filter_jobs(jobs, filters), filters,
        dataset_sha256=hashlib.sha256(raw).hexdigest(), validated_jobs=len(jobs))
    (output / "seattle_remote_view.zip").write_bytes(payload)
    with ZipFile(BytesIO(payload)) as archive:
        for name in archive.namelist():
            (output / name).write_bytes(archive.read(name))
    metadata = {"source": "Automated example generation, not a browser download",
                "zip_sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
    (output / "generation.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/week9-export-example")
    run(parser.parse_args().output.resolve())
