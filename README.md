# QML-SleepNet — reproducible research implementation

**Quantum machine learning, causal inference and CNN-BiLSTM modelling for minute-level sleep-apnea detection using Apnea-ECG**

This repository presents the implemented research pipeline, model artifacts, evaluation evidence and reproducibility utilities for QML-SleepNet. The methodological specification is documented in `docs/METHODOLOGY_ALIGNMENT.md`, while the five source diagrams supplied for the project are preserved under `guide_source/` with SHA-256 verification in `config/guide_source_manifest.json`.

## System definitions

Three related model configurations are reported separately to avoid ambiguity:

| System | Definition | Role |
|---|---|---|
| Stage06 hybrid model | `qml_sleepnet_final_guide_corrected.pt` | single binary Apnea-vs-Normal checkpoint combining QML, temporal and causal representations |
| Reference QML system | fixed equal-logit QML evaluation configuration | QML-focused comparison system used in the final evaluation |
| Final integrated system | fixed 25% physiology + 75% QML logit fusion | final QML-inclusive evaluation configuration; official-x accuracy **90.8627%** |

These systems are evaluated and reported independently; the final integrated system is not represented as the same object as the Stage06 checkpoint.

## Implemented methodology

```text
prepared Stage02 ECG / minute windows
        ↓
Stage03 physiological feature bank
        ↓
ANOVA → mRMR → SHAP → PCA128
        ↓
MLP 128 → 64 → 32 → 8
        ↓
Stage04 QML: Angle-Rx / IQP + VQC + fidelity-kernel QSVC + quantum-transformer evaluation
        ↓
Stage05 PC / FCI / NOTEARS / LiNGAM + SCM + interventions / ACE → causal16
        ↓
Stage06 QML8 + CNN-BiLSTM temporal512 + causal gate16
        ↓
536 → 256 → 128 → 64 → 2 logits
```

The Stage04 implementation uses 8 qubits, VQC depth 4, 96 variational quantum parameters, CNOT entanglement, Rz-Ry-Rz rotations and Pauli-Z expectation measurements. The Stage06 temporal branch uses parallel Conv1D kernels, a two-layer bidirectional LSTM, self-attention and a causal-aware fusion pathway.

## Scope and methodological constraints

- **OSA / CSA / Mixed subtype classification is not claimed.** The minute-level supervision available to this implementation is Apnea/Normal.
- **AHI is not used as an input feature.** Deriving AHI from the same A/N annotations would introduce target leakage.
- **No quantum-advantage claim is made.** Quantum components are evaluated as part of the proposed hybrid methodology.
- The final integrated official-x result is reported as project-level evaluation evidence rather than pristine prospective external validation.

## Reproducibility path 1 — repository verification

```bash
pip install -r requirements-verify.txt
python scripts/run_pipeline.py --mode verify
```

This verifies the source-diagram hashes, model/input artifact hashes, methodological invariants, result contracts, notebook syntax and repository tests. No training or dataset labels are required.

## Reproducibility path 2 — Stage06 inference

The repository includes the Stage04 bridge/QML checkpoints, the Stage06 model checkpoint, the QML8 and causal16 arrays consumed by Stage06, and the Stage06 reference probabilities. Prepared Stage02 ECG `.npz` records remain external.

```bash
pip install -r requirements-inference.txt
python scripts/run_pipeline.py --mode inference \
  --stage02-dir /path/to/stage02_preprocessed \
  --compare-reference
```

A numerical reproduction test was completed on the `x01` Stage02 record. All **522 minute rows** reproduced the stored Stage06 probabilities with maximum absolute difference `9.5367431640625e-07` on CPU, without accessing official-x labels. The machine-readable receipt is `results/validation/FROZEN_STAGE06_X01_REPRODUCTION.json`.

## Reproducibility path 3 — methodology replay

```bash
python scripts/run_pipeline.py --mode methodology-replay --workspace /path/to/QML_SleepNet
```

This is a prepared-workspace replay rather than a raw-data one-click build. Stage03 requires existing Stage02 outputs and the recorded label-free feature cache used by the research pipeline. The runner verifies the expected source state before recomputation and stops if the available workspace would select a different cache.

## Final evaluation

For the final integrated QML-inclusive system:

- official-x: `35` records / `17,248` scored rows;
- accuracy: `0.9086270871985158` (90.8627%);
- balanced accuracy: `0.9076848836674374`;
- F1: `0.882475764354959`;
- MCC: `0.8084026100817799`;
- AUROC: `0.9675236374617686`;
- AUPRC: `0.9497755803318464`;
- prediction SHA-256: `063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f`.

The classical physiology-only comparator attains slightly higher raw official-x accuracy (91.0192%); this comparison is retained transparently in the evaluation tables.

## Repository structure

```text
QML-SleepNet/
├── guide_source/                    # archived source diagrams retained for provenance
├── config/                          # execution, methodology and result contracts
├── pretrained/                      # versioned model checkpoints + SHA-256 records
├── precomputed/stage06_inputs/      # QML8 / causal16 arrays used by Stage06
├── notebooks/guide/                 # original methodology-stage notebooks (legacy path retained)
├── notebooks/evidence/              # QML evaluation and interpretability evidence
├── notebooks/promoted_evidence/     # final-system evaluation notebooks (legacy path retained)
├── results/                         # evaluation tables, manifests and validation receipts
├── scripts/                         # verification, inference and replay utilities
└── docs/
    ├── METHODOLOGY_ALIGNMENT.md
    ├── INFERENCE.md
    └── FULL_REPRODUCTION.md
```

Historical directory and artifact identifiers are retained where necessary for provenance and executable reproducibility; the academic terminology used in the documentation is defined in `docs/METHODOLOGY_ALIGNMENT.md`.
