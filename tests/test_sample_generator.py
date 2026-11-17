from pathlib import Path

from scripts.generate_sample_data import generate


def test_sample_generation_is_reproducible(tmp_path):
    output = tmp_path / "jobs.csv"
    generate(output)
    bundled = Path(__file__).resolve().parents[1] / "data" / "sample_jobs.csv"
    assert output.read_bytes() == bundled.read_bytes()
