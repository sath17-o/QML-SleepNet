from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "precomputed" / "final_integrated_inputs"
QML_PATH = INPUT_DIR / "FINAL_FIXED_EQUAL_LOGIT_X_PREDICTIONS_FROZEN_BEFORE_SCORING.npz"
PHYS_PATH = INPUT_DIR / "DEV35_STAGE15A_PHYSIO_BOOSTING_X_PREDICTIONS_FROZEN_BEFORE_SCORING.npz"
LABEL_PATH = INPUT_DIR / "OFFICIAL_X_EVALUATION_LABELS.csv"

EXPECTED = {
    "qml_sha256": "f121a79191be00a28f33e06e7dec20cc689268b10a988c52e21284c90d1e2eef",
    "physiology_sha256": "e548af5c1d8ad39f8ea192680ee7ae7af303b993e65f410ea2ee18f015e3e244",
    "labels_sha256": "de7abc9218a902f3867de617cea477e6db7a7de2763fe4db5ba3d0fcf7289730",
    "final_npz_sha256": "063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f",
    "n": 17248,
    "physiology_weight": 0.25,
    "qml_weight": 0.75,
    "hard_threshold": 0.5,
    "accuracy": 0.9086270871985158,
    "balanced_accuracy": 0.9076848836674374,
    "precision": 0.8621594055077955,
    "sensitivity": 0.9037727203299221,
    "specificity": 0.9115970470049528,
    "f1": 0.882475764354959,
    "mcc": 0.8084026100817799,
    "auroc": 0.9675236374617686,
    "auprc": 0.9497755803318464,
    "brier": 0.0796448443135515,
    "nll": 0.4334665417947636,
    "tn": 9755,
    "fp": 946,
    "fn": 630,
    "tp": 5917,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_file(path: Path, expected_hash: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"Missing required file: {path}")
    actual = sha256(path)
    if actual != expected_hash:
        raise RuntimeError(f"SHA-256 mismatch for {path.name}: expected={expected_hash} got={actual}")
    print(f"PASS input {path.name} {actual}")


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=np.float64), 1e-12, 1.0 - 1e-12)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def load_labels(path: Path) -> tuple[np.ndarray, np.ndarray]:
    uids: list[str] = []
    labels: list[int] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["uid", "y_true"]:
            raise RuntimeError(f"Unexpected labels schema: {reader.fieldnames}")
        for row in reader:
            uids.append(row["uid"])
            labels.append(int(row["y_true"]))
    return np.asarray(uids, dtype=str), np.asarray(labels, dtype=np.int8)


def metric_dict(y_true: np.ndarray, probability: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    return {
        "n": int(y_true.size),
        "accuracy": float(accuracy_score(y_true, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, prediction)),
        "precision": float(precision_score(y_true, prediction)),
        "sensitivity": float(recall_score(y_true, prediction)),
        "specificity": float(tn / (tn + fp)),
        "f1": float(f1_score(y_true, prediction)),
        "mcc": float(matthews_corrcoef(y_true, prediction)),
        "auroc": float(roc_auc_score(y_true, probability)),
        "auprc": float(average_precision_score(y_true, probability)),
        "brier": float(brier_score_loss(y_true, probability)),
        "nll": float(log_loss(y_true, np.column_stack([1.0 - probability, probability]), labels=[0, 1])),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def assert_metrics(actual: dict[str, float | int]) -> None:
    exact_ints = ["n", "tn", "fp", "fn", "tp"]
    floats = [
        "accuracy", "balanced_accuracy", "precision", "sensitivity", "specificity",
        "f1", "mcc", "auroc", "auprc", "brier", "nll",
    ]
    for key in exact_ints:
        if int(actual[key]) != int(EXPECTED[key]):
            raise RuntimeError(f"Metric mismatch for {key}: expected={EXPECTED[key]} got={actual[key]}")
    for key in floats:
        if not np.isclose(float(actual[key]), float(EXPECTED[key]), rtol=0.0, atol=1e-12):
            raise RuntimeError(f"Metric mismatch for {key}: expected={EXPECTED[key]} got={actual[key]}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Reproduce the final 25% physiology + 75% QML integrated evaluation configuration.")
    ap.add_argument("--output", default="outputs/final_integrated_predictions.npz")
    ap.add_argument("--metrics-output", default="outputs/final_integrated_metrics.json")
    args = ap.parse_args()

    check_file(QML_PATH, EXPECTED["qml_sha256"])
    check_file(PHYS_PATH, EXPECTED["physiology_sha256"])
    check_file(LABEL_PATH, EXPECTED["labels_sha256"])

    qml = np.load(QML_PATH, allow_pickle=False)
    phys = np.load(PHYS_PATH, allow_pickle=False)

    required_qml = {"test_uids", "ensemble_hmm_logit_mean"}
    required_phys = {"test_uids", "hmm_apnea_posterior"}
    if not required_qml.issubset(qml.files):
        raise RuntimeError(f"QML parent missing fields: {sorted(required_qml - set(qml.files))}")
    if not required_phys.issubset(phys.files):
        raise RuntimeError(f"Physiology parent missing fields: {sorted(required_phys - set(phys.files))}")

    qml_uids = np.asarray(qml["test_uids"], dtype=str)
    phys_uids = np.asarray(phys["test_uids"], dtype=str)
    if qml_uids.size != EXPECTED["n"] or phys_uids.size != EXPECTED["n"]:
        raise RuntimeError("Parent row count does not match the published 17,248-row contract")
    if not np.array_equal(qml_uids, phys_uids):
        raise RuntimeError("QML and physiology parent UIDs are not exactly aligned")

    physiology = np.asarray(phys["hmm_apnea_posterior"], dtype=np.float64)
    qml_probability = np.asarray(qml["ensemble_hmm_logit_mean"], dtype=np.float64)
    w_phys = np.float64(EXPECTED["physiology_weight"])
    w_qml = np.float64(EXPECTED["qml_weight"])
    threshold = np.float64(EXPECTED["hard_threshold"])

    # Fixed project-level fusion: weighted mean in logit space, then sigmoid.
    fused_probability = sigmoid(w_phys * logit(physiology) + w_qml * logit(qml_probability))
    prediction = (fused_probability >= threshold).astype(np.int8)

    output = (ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        test_uids=qml_uids,
        physiology_hmm_posterior=physiology,
        qml_core3_hmm_logit_mean=qml_probability,
        physiology_weight=w_phys,
        qml_weight=w_qml,
        fused_probability=fused_probability,
        prediction=prediction,
        hard_threshold=threshold,
    )

    final_hash = sha256(output)
    if final_hash != EXPECTED["final_npz_sha256"]:
        raise RuntimeError(
            f"Final prediction artifact hash mismatch: expected={EXPECTED['final_npz_sha256']} got={final_hash}"
        )

    # Official-x labels are deliberately loaded only after predictions have been fixed and hashed.
    label_uids, y_true = load_labels(LABEL_PATH)
    if not np.array_equal(label_uids, qml_uids):
        raise RuntimeError("Evaluation-label UIDs are not exactly aligned with the fixed prediction UIDs")
    if y_true.size != EXPECTED["n"]:
        raise RuntimeError("Evaluation label row count mismatch")

    metrics = metric_dict(y_true, fused_probability, prediction)
    assert_metrics(metrics)

    metrics_output = (ROOT / args.metrics_output).resolve()
    metrics_output.parent.mkdir(parents=True, exist_ok=True)
    metrics_output.write_text(json.dumps({
        "system": "Final integrated QML-inclusive project-level evaluation configuration",
        "physiology_weight": float(w_phys),
        "qml_weight": float(w_qml),
        "fusion": "weighted logit mean followed by sigmoid",
        "hard_threshold": float(threshold),
        "official_x_labels_used_for_fusion_or_model_selection": False,
        "official_x_labels_loaded_only_after_predictions_fixed": True,
        "prediction_artifact_sha256": final_hash,
        "metrics": metrics,
    }, indent=2) + "\n", encoding="utf-8")

    print("\nFINAL INTEGRATED SYSTEM REPRODUCTION")
    print(f"Rows: {metrics['n']}")
    print(f"Physiology weight: {w_phys}")
    print(f"QML weight: {w_qml}")
    print("Fusion: weighted logit mean followed by sigmoid")
    print(f"Hard threshold: {threshold}")
    print("Official-x labels used for fusion/model selection: NO")
    print("Official-x labels loaded for scoring only after predictions were fixed: YES")
    print(f"Accuracy: {metrics['accuracy']:.16f}")
    print(f"Balanced accuracy: {metrics['balanced_accuracy']:.16f}")
    print(f"F1: {metrics['f1']:.16f}")
    print(f"MCC: {metrics['mcc']:.16f}")
    print(f"AUROC: {metrics['auroc']:.16f}")
    print(f"AUPRC: {metrics['auprc']:.16f}")
    print(f"TN={metrics['tn']} FP={metrics['fp']} FN={metrics['fn']} TP={metrics['tp']}")
    print(f"Prediction artifact SHA-256: {final_hash}")
    print(f"Wrote predictions -> {output}")
    print(f"Wrote metrics -> {metrics_output}")
    print("FINAL INTEGRATED REPRODUCTION PASS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
