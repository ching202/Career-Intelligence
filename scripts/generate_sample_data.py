"""Generate fictional demonstration records; no job board or personal data is used."""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ["job_id", "title", "company", "location", "work_mode", "experience_level",
           "salary_min", "salary_max", "salary_currency", "salary_period", "skills",
           "posted_date", "data_source"]
ROLES = [
    ("Backend Developer", ["Python", "SQL", "FastAPI", "Docker"]),
    ("Frontend Developer", ["JavaScript", "TypeScript", "React", "CSS"]),
    ("Full Stack Developer", ["TypeScript", "JavaScript", "Node.js", "SQL"]),
    ("Software Engineer", ["Java", "Spring", "SQL", "Git"]),
    ("Platform Engineer", ["Go", "Python", "Kubernetes", "Linux"]),
    ("Mobile Developer", ["Kotlin", "Java", "Git"]),
    ("iOS Developer", ["Swift", "Git"]),
    ("Applications Developer", ["C#", ".NET", "SQL", "Azure"]),
    ("Systems Developer", ["C++", "C", "Rust", "Linux"]),
    ("Data Software Engineer", ["Python", "SQL", "Pandas", "AWS"]),
]
LOCATIONS = ["Seattle, WA", "Rockville, MD", "Washington, DC", "Austin, TX", "Boston, MA",
             "New York, NY", "San Francisco, CA", "Chicago, IL", "Atlanta, GA", "Remote - US"]


def generate(path: Path, rows: int = 300, seed: int = 450) -> None:
    rng = random.Random(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        for i in range(rows):
            title, skills = rng.choice(ROLES)
            level = rng.choices(["Internship", "Entry", "Mid", "Senior", "Lead"], [1, 4, 5, 4, 1])[0]
            base = {"Internship": 45000, "Entry": 70000, "Mid": 100000, "Senior": 135000, "Lead": 165000}[level]
            low = base + rng.randrange(-10000, 20001, 1000)
            high = low + rng.randrange(10000, 40001, 1000)
            location = rng.choice(LOCATIONS)
            mode = "Remote" if location == "Remote - US" else rng.choices(["Remote", "Hybrid", "On-site"], [3, 4, 3])[0]
            period = "hourly" if i % 7 == 0 else "monthly" if i % 19 == 0 else "weekly" if i % 23 == 0 else "annual"
            divisor = {"annual": 1, "hourly": 2080, "monthly": 12, "weekly": 52}[period]
            salary_min, salary_max = round(low / divisor, 2), round(high / divisor, 2)
            if i % 11 == 0:
                salary_min = salary_max = ""
            # A few non-USD rows demonstrate honest exclusion from salary comparisons.
            currency = "CAD" if i % 29 == 0 else "USD"
            selected_skills = list(skills)
            if rng.random() > 0.5:
                selected_skills.append(rng.choice(["Docker", "AWS", "Git", "SQL"]))
            writer.writerow({
                "job_id": f"SAMPLE-{i + 1:04d}", "title": title,
                "company": f"Fictional Studio {rng.randrange(1, 31):02d}",
                "location": location, "work_mode": mode, "experience_level": level,
                "salary_min": salary_min, "salary_max": salary_max,
                "salary_currency": currency, "salary_period": period,
                "skills": ";".join(sorted(set(selected_skills))),
                "posted_date": (date(2026, 9, 1) + timedelta(days=rng.randrange(60))).isoformat(),
                "data_source": "Synthetic sample; not real vacancies",
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "sample_jobs.csv")
    parser.add_argument("--rows", type=int, default=300)
    parser.add_argument("--seed", type=int, default=450)
    args = parser.parse_args()
    if args.rows < 1 or args.rows > 50000:
        parser.error("--rows must be between 1 and 50000")
    generate(args.output, args.rows, args.seed)
    print(f"Generated {args.rows} synthetic records at {args.output}")
