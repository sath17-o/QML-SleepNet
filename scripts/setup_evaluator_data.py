from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD_MANIFEST = ROOT / "data" / "STAGE02_OFFICIAL_X_SHA256.csv"
DATA_DIR = ROOT / "data" / "stage02_official_x"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_record_manifest() -> dict[str, dict[str, str]]:
    with RECORD_MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 35:
        raise RuntimeError(f"Record checksum manifest must contain 35 rows; found {len(rows)}")
    expected = [f"x{i:02d}_preprocessed.npz" for i in range(1, 36)]
    if [row["file"] for row in rows] != expected:
        raise RuntimeError("Record checksum manifest is not ordered x01 through x35")
    return {row["file"]: row for row in rows}


def verify_records(names: list[str], records: dict[str, dict[str, str]]) -> None:
    failures: list[str] = []
    for name in names:
        expected = records.get(name)
        if expected is None:
            failures.append(f"manifest entry missing: {name}")
            continue
        path = DATA_DIR / name
        if not path.is_file():
            failures.append(f"file missing: {path}")
            continue
        size = path.stat().st_size
        if size != int(expected["bytes"]):
            failures.append(f"size mismatch: {name} expected={expected['bytes']} got={size}")
            continue
        digest = sha256(path)
        if digest != expected["sha256"]:
            failures.append(f"SHA-256 mismatch: {name} expected={expected['sha256']} got={digest}")
            continue
        print(f"PASS {name} {digest}")
    if failures:
        raise RuntimeError("Stage02 record verification failed:\n  - " + "\n  - ".join(failures))


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify the Stage02 evaluator records bundled with QML-SleepNet.")
    ap.add_argument("--mode", choices=["demo", "full"], default="full")
    args = ap.parse_args()

    records = load_record_manifest()
    if args.mode == "demo":
        expected_records = ["x01_preprocessed.npz"]
    else:
        expected_records = [f"x{i:02d}_preprocessed.npz" for i in range(1, 36)]

    verify_records(expected_records, records)
    print(f"EVALUATOR DATA READY: {len(expected_records)} verified Stage02 record(s)")
    print(f"Directory: {DATA_DIR}")
    print(f"Mode: {args.mode}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
