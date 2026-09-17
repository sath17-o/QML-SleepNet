# QML-SleepNet

**Quantum machine learning, causal inference and CNN-BiLSTM modelling for minute-level sleep-apnea detection on the PhysioNet Apnea-ECG dataset**

[![Verify reproducibility package](https://github.com/sath17-o/QML-SleepNet/actions/workflows/verify.yml/badge.svg)](https://github.com/sath17-o/QML-SleepNet/actions/workflows/verify.yml)

QML-SleepNet is a research implementation that combines physiological feature engineering, quantum-machine-learning evaluation, causal analysis and a CNN-BiLSTM temporal pathway for binary **Apnea vs Normal** classification. The repository contains the implemented methodology, versioned model/input artifacts, evaluation evidence and evaluator-facing reproduction utilities.

The repository is intentionally explicit about what is executable and what is not. It provides reproducible **inference and evaluation replay** from versioned research artifacts; it does not claim a one-command raw-PhysioNet-to-training rebuild.

## Evaluator quick start

A normal clone is sufficient. The prepared Stage02 official-test records `x01`–`x35`, the Stage06 checkpoint and the final-integration parent predictions are versioned directly in the repository. No Google Drive, Git LFS or separate evaluator data download is required.

### Prerequisite

- Windows: Python **3.11** with the standard `py` launcher.
- Internet access is needed only when the local virtual environment must install dependencies.

```bat
git clone https://github.com/sath17-o/QML-SleepNet.git
cd QML-SleepNet
```

### Three executable evaluator paths

| Command | What it executes | Expected successful terminal condition |
|---|---|---|
| `RUN_DEMO.bat` | Stage06 inference on `x01` and comparison with stored Stage06 reference probabilities | `DEMO PASS: x01 reproduced the stored Stage06 probabilities.` |
| `RUN_FULL_EVALUATION.bat` | Stage06 inference on all `x01`–`x35` prepared records, producing `17,248` probabilities without reading official-test labels | `FULL EVALUATION PASS: all official-x reference probabilities reproduced within tolerance.` |
| `RUN_FINAL_INTEGRATED_EVALUATION.bat` | Final fixed 25% physiology + 75% QML weighted-logit evaluation replay over all `17,248` aligned UIDs | `FINAL INTEGRATED EVALUATION PASS` |

Detailed execution notes are in [`docs/EVALUATOR_RUN.md`](docs/EVALUATOR_RUN.md) and [`docs/FINAL_INTEGRATED_EVALUATION.md`](docs/FINAL_INTEGRATED_EVALUATION.md).

## What is reproducible from this repository

| Reproduction path | Starting point | What is recomputed | Label use |
|---|---|---|---|
| Repository verification | versioned repository artifacts | hashes, methodological invariants, result contracts, notebook syntax and tests | no dataset labels required |
| Stage06 checkpoint reproduction | prepared Stage02 ECG + versioned QML8/causal16 inputs + Stage06 checkpoint | Stage06 probabilities | official-x labels are **not read** |
| Final integrated evaluation replay | versioned physiology and QML parent predictions | fixed 25/75 logit fusion, hard predictions and metrics | labels are loaded **only for scoring after predictions are fixed** |
| Methodology replay | prepared research workspace | downstream methodology stages from recorded prepared inputs | depends on the stage being replayed |

The final integrated replay has been validated both on a Windows checkout and on GitHub Actions Ubuntu. The CI workflow also deliberately rewrites the scoring-label CSV with Windows-style CRLF line endings and reruns the complete final replay to verify cross-platform integrity handling.

## Reported final integrated result

The final project-level QML-inclusive evaluation configuration uses:

```text
z_final = 0.25 × logit(p_physiology) + 0.75 × logit(p_QML)
p_final = sigmoid(z_final)
prediction = 1 if p_final >= 0.5 else 0
```

Evaluation set: **35 official-test records / 17,248 scored minute rows**.

| Metric | Value |
|---|---:|
| Accuracy | **0.9086270871985158 (90.8627%)** |
| Balanced accuracy | 0.9076848836674374 |
| Precision | 0.8621594055077955 |
| Sensitivity | 0.9037727203299221 |
| Specificity | 0.9115970470049528 |
| F1 | 0.8824757643549590 |
| MCC | 0.8084026100817799 |
| AUROC | 0.9675236374617686 |
| AUPRC | 0.9497755803318464 |
| Brier score | 0.0796448443135515 |
| NLL | 0.4334665417947636 |

Confusion matrix:

```text
TN = 9755    FP = 946
FN =  630    TP = 5917
```

The classical physiology-only comparator has raw official-x accuracy **91.0192%**; the reference QML system has accuracy **90.1148%**. These comparisons are retained transparently rather than being presented as evidence of quantum advantage.

## Three model identities kept separate

The repository distinguishes three related configurations to prevent metric/model ambiguity:

| System | Definition | Role |
|---|---|---|
| **Stage06 hybrid model** | `pretrained/stage06/qml_sleepnet_final_guide_corrected.pt` | Single binary checkpoint combining QML, temporal and causal representations |
| **Reference QML system** | fixed equal-logit QML evaluation configuration | QML-focused parent/comparison system used in later evaluation |
| **Final integrated system** | fixed `0.25 physiology + 0.75 QML` fusion in logit space | Final project-level QML-inclusive evaluation configuration |

The **90.8627%** result belongs to the final integrated system. It is not the accuracy of the Stage06 checkpoint.

## Implemented methodology

The implemented research sequence is:

```text
PhysioNet Apnea-ECG
        ↓
prepared 60-s Stage02 ECG windows
        ↓
physiological feature engineering
        ↓
ANOVA → mRMR → SHAP → PCA128
        ↓
neural bridge 128 → 64 → 32 → 8
        ↓
Stage04 QML
Angle-Rx / IQP + VQC + fidelity-kernel QSVC + quantum-transformer evaluation
        ↓
Stage05 causal analysis
PC / FCI / NOTEARS / LiNGAM + SCM + interventions / ACE → causal16
        ↓
Stage06 hybrid model
QML8 + CNN-BiLSTM temporal representation + causal-aware fusion
        ↓
binary Apnea-vs-Normal classification
        ↓
interpretability, robustness and final statistical evaluation
```

The detailed specification-to-implementation mapping is maintained in [`docs/METHODOLOGY_ALIGNMENT.md`](docs/METHODOLOGY_ALIGNMENT.md).

### Stage06 architecture

The Stage06 temporal branch consumes 60-second ECG windows at 100 Hz (`6000` samples). It uses parallel Conv1D kernels (`3`, `5`, `7`), batch normalization, ReLU and temporal pooling, followed by a two-layer bidirectional LSTM and self-attention. Mean/max temporal aggregation forms a `512-D` temporal representation.

The final Stage06 fusion is:

```text
QML8 + temporal512 + gated causal16
              ↓
             536
              ↓
       256 → 128 → 64 → 2 logits
```

The causal gate is generated from the `causal16` branch. The Stage06 task is binary Apnea/Normal classification.

## Reproduction path 1 — repository verification

```bash
python3.11 -m pip install -r requirements-verify.txt
python3.11 scripts/run_pipeline.py --mode verify
```

This verifies versioned model/input hashes, source-diagram provenance, methodological invariants, result contracts, notebook syntax and repository tests. It performs **no training**.

## Reproduction path 2 — Stage06 inference

For a complete manual cross-platform run:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-inference.txt
.venv/bin/python scripts/setup_evaluator_data.py --mode full
.venv/bin/python scripts/run_pipeline.py --mode inference \
  --stage02-dir data/stage02_official_x \
  --device cpu \
  --compare-reference
```

On Windows, `RUN_FULL_EVALUATION.bat` performs the corresponding setup and execution automatically.

The evaluator data integrity check validates all 35 prepared Stage02 files against [`data/STAGE02_OFFICIAL_X_SHA256.csv`](data/STAGE02_OFFICIAL_X_SHA256.csv) before inference. The successful full run writes exactly **17,248** Stage06 rows and requires reference-probability agreement within the published tolerance (`1e-4`).

## Reproduction path 3 — final integrated evaluation

Windows:

```bat
RUN_FINAL_INTEGRATED_EVALUATION.bat
```

Manual cross-platform execution:

```bash
python3.11 -m pip install -r requirements-final-evaluation.txt
python3.11 scripts/run_final_integrated_evaluation.py
```

The runner performs all of the following before declaring success:

1. verifies the exact SHA-256 values of the two binary parent prediction artifacts;
2. verifies the scoring-label content using a canonical LF-normalized SHA-256 so Windows CRLF conversion cannot create a false integrity failure;
3. requires exact QML/physiology UID alignment over `17,248` rows;
4. reconstructs the fixed weighted-logit fusion;
5. checks the exact UID fingerprint, a deterministic `1e-13`-quantized probability fingerprint and the exact hard-prediction fingerprint;
6. loads official-x labels only after the fused predictions have been fixed; and
7. verifies the complete metric/confusion-matrix contract.

The historical frozen prediction artifact has SHA-256:

```text
063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f
```

That is retained as provenance for the historical compressed NPZ. A newly serialized NPZ is not required to have identical container bytes across NumPy/platform combinations; cross-platform equality is established through the semantic fingerprints and metric contract documented in [`config/final_integrated_execution_manifest.json`](config/final_integrated_execution_manifest.json).

## Reproduction path 4 — methodology replay

```bash
python3.11 scripts/run_pipeline.py --mode methodology-replay --workspace /path/to/QML_SleepNet
```

This is a **prepared-workspace methodology replay**, not a raw-data one-click build. Stage03 requires existing Stage02 outputs and the recorded label-free feature cache used by the research pipeline. The runner verifies the expected source state before recomputation and fails closed if the available workspace would select a different cache.

## Scientific scope and reporting boundaries

- **Binary task only:** this implementation predicts Apnea vs Normal at minute level.
- **No OSA / CSA / Mixed subtype claim:** the supervision used here does not provide those subtype labels.
- **AHI is not a model input:** deriving AHI from the same A/N annotations would leak the target.
- **No quantum-advantage claim:** quantum components are evaluated as part of the proposed hybrid methodology, but the repository does not claim that they outperform all classical alternatives.
- **Final integrated result is project-level evaluation evidence:** it is not presented as pristine prospective external validation.
- **No raw-data end-to-end rebuild claim:** the executable Stage06 path starts from prepared Stage02 representations, and the final integrated path starts from versioned parent predictions.
- **A/B/C are not apnea subtypes:** where retained in historical analysis, they represent dataset record/burden categories only.

These boundaries are deliberate: the repository reports only what the available labels, artifacts and executable evidence support.

## Data provenance and integrity

Source dataset: **PhysioNet Apnea-ECG Database v1.0.0**

- DOI: `10.13026/C23W2R`
- Source: <https://physionet.org/content/apnea-ecg/1.0.0/>
- PhysioNet distribution license recorded for this dataset: Open Data Commons Attribution License v1.0

The files under `data/stage02_official_x/` are **project-prepared derivatives** used by the research implementation; they are not presented as raw PhysioNet recordings. Their byte counts and SHA-256 values are fixed in [`data/STAGE02_OFFICIAL_X_SHA256.csv`](data/STAGE02_OFFICIAL_X_SHA256.csv).

## Repository structure

```text
QML-SleepNet/
├── .github/workflows/                 # automated reproducibility verification
├── config/                            # scientific and execution contracts
├── data/
│   └── stage02_official_x/            # prepared x01-x35 evaluator Stage02 records
├── docs/                              # methodology, inference and evaluator documentation
├── guide_source/                      # archived source diagrams retained for provenance
├── notebooks/
│   ├── guide/                         # methodology-stage notebooks; legacy path retained
│   ├── evidence/                      # QML and interpretability evidence
│   └── promoted_evidence/             # final-system evidence; legacy path retained
├── precomputed/
│   ├── stage06_inputs/                # versioned QML8 / causal16 Stage06 inputs
│   └── final_integrated_inputs/       # final-fusion parent predictions + scoring labels
├── pretrained/                        # versioned model checkpoints
├── results/                           # evaluation tables, manifests and validation receipts
├── scripts/                           # verification, inference and replay utilities
├── RUN_DEMO.bat
├── RUN_FULL_EVALUATION.bat
└── RUN_FINAL_INTEGRATED_EVALUATION.bat
```

## Documentation map

| Document | Purpose |
|---|---|
| [`docs/EVALUATOR_RUN.md`](docs/EVALUATOR_RUN.md) | shortest Stage06 evaluator execution path |
| [`docs/FINAL_INTEGRATED_EVALUATION.md`](docs/FINAL_INTEGRATED_EVALUATION.md) | exact final 25/75 fusion replay and metric contract |
| [`docs/METHODOLOGY_ALIGNMENT.md`](docs/METHODOLOGY_ALIGNMENT.md) | mapping from methodological specification to implementation |
| [`docs/INFERENCE.md`](docs/INFERENCE.md) | Stage06 inference inputs, outputs and boundaries |
| [`docs/FULL_REPRODUCTION.md`](docs/FULL_REPRODUCTION.md) | repository verification and broader replay modes |
| [`data/README.md`](data/README.md) | evaluator-data provenance and integrity notes |

## Reproducibility principle

This repository separates **historical evidence**, **executable inference**, **final-system evaluation replay** and **methodology replay** rather than collapsing them into a single claim. That separation is intentional: an evaluator should be able to identify exactly which artifact generated which result, what inputs were used, whether labels were accessed, and which parts of the research chain are being recomputed.