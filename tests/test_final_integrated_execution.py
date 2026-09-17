from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_final_integrated_manifest_contract():
    cfg = json.loads((ROOT / "config" / "final_integrated_execution_manifest.json").read_text(encoding="utf-8"))
    assert cfg["rows"] == 17248
    assert cfg["physiology_weight"] == 0.25
    assert cfg["qml_weight"] == 0.75
    assert cfg["hard_threshold"] == 0.5
    assert cfg["fusion"] == "weighted logit mean followed by sigmoid"
    assert cfg["official_x_labels_used_for_fusion_or_model_selection"] is False
    assert cfg["expected_output"]["sha256"] == "063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f"
    m = cfg["expected_metrics"]
    assert m["accuracy"] == 0.9086270871985158
    assert (m["tn"], m["fp"], m["fn"], m["tp"]) == (9755, 946, 630, 5917)


def test_final_integrated_runner_syntax():
    source = (ROOT / "scripts" / "run_final_integrated_evaluation.py").read_text(encoding="utf-8")
    compile(source, "scripts/run_final_integrated_evaluation.py", "exec")
