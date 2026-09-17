from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_final_integrated_manifest_contract():
    cfg = json.loads((ROOT / "config" / "final_integrated_execution_manifest.json").read_text(encoding="utf-8"))
    assert cfg["schema_version"] == 3
    assert cfg["rows"] == 17248
    assert cfg["physiology_weight"] == 0.25
    assert cfg["qml_weight"] == 0.75
    assert cfg["hard_threshold"] == 0.5
    assert cfg["fusion"] == "weighted logit mean followed by sigmoid"
    assert cfg["official_x_labels_used_for_fusion_or_model_selection"] is False

    labels = cfg["inputs"]["evaluation_labels"]
    assert labels["canonical_lf_sha256"] == "de7abc9218a902f3867de617cea477e6db7a7de2763fe4db5ba3d0fcf7289730"
    assert labels["repository_lf_sha256"] == labels["canonical_lf_sha256"]
    assert "CRLF" in labels["line_ending_policy"]

    sem = cfg["semantic_reproduction_contract"]
    assert sem["uid_sha256"] == "957dd53b9ff7aa03e8b554ea34c426d074259341a980b89d74e752c21158a641"
    assert sem["probability_quantization_scale"] == 10000000000000
    assert sem["probability_quantized_sha256"] == "d82db455a3570b01d212f21d57d99b0f88997caa18ad5770155e411515e3845b"
    assert sem["prediction_sha256"] == "fe3f3d2da3c6d2993ec3dbe50749e8512e606bfeb1dbb2c0a06be9a71f5ca9fd"

    hist = cfg["historical_reference_artifact"]
    assert hist["sha256"] == "063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f"

    m = cfg["expected_metrics"]
    assert m["accuracy"] == 0.9086270871985158
    assert (m["tn"], m["fp"], m["fn"], m["tp"]) == (9755, 946, 630, 5917)


def test_final_integrated_runner_syntax():
    source = (ROOT / "scripts" / "run_final_integrated_evaluation.py").read_text(encoding="utf-8")
    compile(source, "scripts/run_final_integrated_evaluation.py", "exec")
    assert "canonical_lf_sha256" in source
    assert "check_label_file" in source
