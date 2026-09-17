# Final integrated evaluation replay

The final reported project-level QML-inclusive configuration is a fixed fusion of two already-established parent systems:

- physiology parent: Stage15A physiology-only system;
- QML parent: fixed equal-logit QML system;
- fusion: `0.25 * logit(physiology) + 0.75 * logit(QML)`, followed by sigmoid;
- hard threshold: `0.5`.

The parent official-test prediction artifacts were frozen before scoring. This executable replay does **not** retrain either parent model and does not represent a raw-data end-to-end reconstruction. It deterministically reconstructs the final fusion from the versioned parent predictions and then scores the fixed predictions.

## Windows

From the repository root:

```bat
RUN_FINAL_INTEGRATED_EVALUATION.bat
```

Successful execution must end with:

```text
FINAL INTEGRATED REPRODUCTION PASS
FINAL INTEGRATED EVALUATION PASS
```

The script first verifies the SHA-256 values of the two parent prediction artifacts and the evaluation-label file. It then aligns both parents by UID, computes the fixed weighted logit fusion, writes `outputs/final_integrated_predictions.npz`, and requires its SHA-256 to equal:

```text
063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f
```

Only after the prediction artifact is fixed and hashed are the official-test labels loaded for metric computation. The labels are not used for parent training, fusion-weight selection, threshold selection, or model selection in this replay.

## Published reproduction contract

Expected rows: `17,248`

Expected metrics:

- accuracy: `0.9086270871985158`
- balanced accuracy: `0.9076848836674374`
- precision: `0.8621594055077955`
- sensitivity: `0.9037727203299221`
- specificity: `0.9115970470049528`
- F1: `0.882475764354959`
- MCC: `0.8084026100817799`
- AUROC: `0.9675236374617686`
- AUPRC: `0.9497755803318464`
- Brier score: `0.0796448443135515`
- NLL: `0.4334665417947636`
- confusion matrix: `TN=9755, FP=946, FN=630, TP=5917`

The machine-readable contract is `config/final_integrated_execution_manifest.json`.

## Scope

This is an executable reproduction of the final **project-level evaluation configuration**. It is separate from `RUN_FULL_EVALUATION.bat`, which reproduces the Stage06 hybrid checkpoint probabilities from prepared Stage02 ECG records.
