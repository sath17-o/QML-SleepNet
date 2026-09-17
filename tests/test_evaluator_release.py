from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_evaluator_release_contract_is_complete_and_consistent():
    cfg = json.loads((ROOT / "config" / "stage02_release_manifest.json").read_text(encoding="utf-8"))
    assert cfg["repository"] == "sath17-o/QML-SleepNet"
    assert cfg["release_tag"] == "evaluator-data-v1"
    assert cfg["record_count"] == 35
    assert cfg["source_total_bytes"] == 387049133
    assert len(cfg["assets"]) == 5

    expected_asset_names = [
        "QML-SleepNet_stage02_official_x_part1_x01-x07.zip",
        "QML-SleepNet_stage02_official_x_part2_x08-x14.zip",
        "QML-SleepNet_stage02_official_x_part3_x15-x21.zip",
        "QML-SleepNet_stage02_official_x_part4_x22-x28.zip",
        "QML-SleepNet_stage02_official_x_part5_x29-x35.zip",
    ]
    assert [a["file"] for a in cfg["assets"]] == expected_asset_names
    for asset in cfg["assets"]:
        assert int(asset["bytes"]) > 0
        assert len(asset["sha256"]) == 64
        int(asset["sha256"], 16)

    with (ROOT / "data" / "STAGE02_OFFICIAL_X_SHA256.csv").open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 35
    assert [r["file"] for r in rows] == [f"x{i:02d}_preprocessed.npz" for i in range(1, 36)]
    assert sum(int(r["bytes"]) for r in rows) == cfg["source_total_bytes"]
    for row in rows:
        assert int(row["bytes"]) > 0
        assert len(row["sha256"]) == 64
        int(row["sha256"], 16)


def test_evaluator_release_preparation_receipt_matches_contract():
    receipt = json.loads((ROOT / "results" / "validation" / "STAGE02_RELEASE_PREPARATION_VALIDATION.json").read_text(encoding="utf-8"))
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


def test_evaluator_setup_script_is_syntax_valid():
    source = (ROOT / "scripts" / "setup_evaluator_data.py").read_text(encoding="utf-8")
    compile(source, "scripts/setup_evaluator_data.py", "exec")
