from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "stage02_official_x"
MANIFEST = ROOT / "data" / "STAGE02_OFFICIAL_X_SHA256.csv"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _manifest_rows():
    with MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def test_bundled_evaluator_manifest_is_complete_and_consistent():
    rows = _manifest_rows()
    assert len(rows) == 35
    assert [r["file"] for r in rows] == [f"x{i:02d}_preprocessed.npz" for i in range(1, 36)]
    assert sum(int(r["bytes"]) for r in rows) == 387049133
    for row in rows:
        assert int(row["bytes"]) > 0
        assert len(row["sha256"]) == 64
        int(row["sha256"], 16)


def test_all_bundled_stage02_records_are_present_and_match_manifest():
    rows = _manifest_rows()
    assert DATA_DIR.is_dir()
    actual = sorted(p.name for p in DATA_DIR.glob("x*_preprocessed.npz"))
    assert actual == [r["file"] for r in rows]
    for row in rows:
        path = DATA_DIR / row["file"]
        assert path.stat().st_size == int(row["bytes"])
        assert _sha256(path) == row["sha256"]


def test_bundled_data_validation_receipt_matches_contract():
    receipt = json.loads((ROOT / "results" / "validation" / "STAGE02_BUNDLED_DATA_VALIDATION.json").read_text(encoding="utf-8"))
    assert receipt["stage02_record_count"] == 35
    assert receipt["stage02_total_bytes"] == 387049133
    assert receipt["stage02_sampling_rate_hz"] == 100
    assert receipt["stage02_epoch_seconds"] == 60
    assert receipt["stage06_official_x_uid_count"] == 17248
    assert receipt["stage06_official_x_records"] == 35
    assert receipt["all_stage02_files_have_required_fields"] is True
    assert receipt["all_stage02_geometries_valid"] is True
    assert receipt["all_stage06_uids_resolve_to_stage02_epochs"] is True
    assert receipt["official_x_labels_accessed"] is False


def test_evaluator_data_verifier_is_syntax_valid():
    source = (ROOT / "scripts" / "setup_evaluator_data.py").read_text(encoding="utf-8")
    compile(source, "scripts/setup_evaluator_data.py", "exec")
