"""Create a clean ZIP; omit environments, personal data, and internal Git files."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "htmlcov", "local-runs", "private"}


def package(destination: Path):
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            relative = path.relative_to(ROOT)
            if not path.is_file() or any(part in EXCLUDED for part in relative.parts):
                continue
            if path.name in {".coverage", ".env", "secrets.toml", "package.json"} or path.suffix in {".log", ".pyc", ".zip"}:
                continue
            archive.write(path, Path(ROOT.name) / relative)
    print(destination.resolve())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT.parent / "Career-Intelligence.zip")
    package(parser.parse_args().output)
