from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "stage02_release_manifest.json"
RECORD_MANIFEST = ROOT / "data" / "STAGE02_OFFICIAL_X_SHA256.csv"
DATA_DIR = ROOT / "data" / "stage02_official_x"
CACHE_DIR = ROOT / "data" / ".evaluator_release_cache"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_suffix(destination.suffix + ".part")
    if tmp.exists():
        tmp.unlink()
    request = urllib.request.Request(url, headers={"User-Agent": "QML-SleepNet-evaluator-setup/1.0"})
    print(f"Downloading {destination.name} ...", flush=True)
    try:
        with urllib.request.urlopen(request) as response, tmp.open("wb") as out:
            shutil.copyfileobj(response, out, length=1024 * 1024)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    os.replace(tmp, destination)


def safe_extract_stage02(archive: Path) -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    extracted = 0
    with zipfile.ZipFile(archive, "r") as zf:
        for member in zf.infolist():
            if member.is_dir():
                continue
            p = PurePosixPath(member.filename)
            if len(p.parts) != 2 or p.parts[0] != "stage02_official_x":
                # Release archives may contain provenance files at their root;
                # only the declared Stage02 directory is extracted.
                continue
            name = p.parts[1]
            if not (name.startswith("x") and name.endswith("_preprocessed.npz")):
                continue
            target = DATA_DIR / name
            with zf.open(member, "r") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
            extracted += 1
    return extracted


def load_record_manifest() -> dict[str, dict[str, str]]:
    with RECORD_MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 35:
        raise RuntimeError(f"Record checksum manifest must contain 35 rows; found {len(rows)}")
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
            failures.append(f"SHA-256 mismatch: {name}")
    if failures:
        raise RuntimeError("Stage02 record verification failed:\n  - " + "\n  - ".join(failures))


def main() -> None:
    ap = argparse.ArgumentParser(description="Download and verify QML-SleepNet evaluator Stage02 data from the repository release.")
    ap.add_argument("--mode", choices=["demo", "full"], default="full")
    ap.add_argument("--refresh", action="store_true", help="Redownload release assets even when a verified cached copy is present.")
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    repo = cfg["repository"]
    tag = cfg["release_tag"]
    assets = cfg["assets"][:1] if args.mode == "demo" else cfg["assets"]
    expected_records = [f"x{i:02d}_preprocessed.npz" for i in range(1, 8 if args.mode == "demo" else 36)]
    record_manifest = load_record_manifest()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for asset in assets:
        filename = asset["file"]
        local = CACHE_DIR / filename
        expected_size = int(asset["bytes"])
        expected_sha = asset["sha256"]
        verified_cache = local.is_file() and local.stat().st_size == expected_size and sha256(local) == expected_sha
        if args.refresh or not verified_cache:
            url = f"https://github.com/{repo}/releases/download/{tag}/{filename}"
            download(url, local)
        if local.stat().st_size != expected_size:
            raise RuntimeError(f"Release asset size mismatch for {filename}")
        actual_sha = sha256(local)
        if actual_sha != expected_sha:
            raise RuntimeError(f"Release asset SHA-256 mismatch for {filename}: {actual_sha}")
        print(f"PASS release asset {filename} {actual_sha}")
        count = safe_extract_stage02(local)
        print(f"Extracted {count} Stage02 records from {filename}")

    verify_records(expected_records, record_manifest)
    print(f"EVALUATOR DATA READY: {len(expected_records)} verified Stage02 records")
    print(f"Directory: {DATA_DIR}")
    print(f"Mode: {args.mode}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
