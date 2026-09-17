# QML-SleepNet — guide-locked reproducibility repository

**Quantum machine learning + causal inference + CNN-BiLSTM for Apnea-ECG sleep-apnea detection**

This repository is source-locked to the **five supplied guide screenshots** in `guide_source/`. The screenshots are hashed in `config/guide_source_manifest.json`; `docs/GUIDE_ALIGNMENT.md` records exactly what is implemented, what was adapted to avoid leakage, what is evidence-only, and what is **not supported / not claimed**.

## Scientific identity: do not conflate these three systems

| Object | What it is | Role |
|---|---|---|
| Guide-native Stage06 | frozen `qml_sleepnet_final_guide_corrected.pt` | direct endpoint of the implemented guide core, Task A binary Apnea vs Normal |
| Canonical reported QML | fixed equal-logit evaluation wrapper | project evaluation system; separate from the single Stage06 checkpoint |
| Promoted final | fixed 25% physiology + 75% canonical-QML logit fusion | later project-level extension; official-x accuracy **90.8627%** |

The promoted system is retained because it is the project's designated final evidence result, but it is **not relabeled as the guide-native Stage06 model**.

## Guide-native implemented core

```text
prepared Stage02 ECG / minute windows
        ↓
Stage03 feature bank
        ↓
ANOVA → mRMR → SHAP → PCA128
        ↓
MLP 128 → 64 → 32 → 8
        ↓
Stage04 QML: Angle/IQP + VQC + fidelity-kernel/QSVC + QT evidence
        ↓
Stage05 PC/FCI/NOTEARS/LiNGAM + SCM + interventions/ACE → causal16
        ↓
Stage06 QML8 + CNN-BiLSTM temporal512 + causal gate16
        ↓
536 → 256 → 128 → 64 → 2 logits
```

The frozen Stage04 audited manifest locks 8 qubits, VQC depth 4, 96 quantum parameters, StronglyEntanglingLayers/CNOT, Rz–Ry–Rz and Pauli-Z expectations. The frozen Stage06 manifest locks Conv1D64 kernels 3/5/7, BiLSTM128×2, self-attention, causal gating and the binary Task-A head.

## Two deliberate scientific non-claims

- **OSA / CSA / Mixed is not trained or claimed.** The available Apnea-ECG minute target used by this project is A/N; inventing subtype ground truth would be invalid.
- **AHI is not used as an input feature.** Although AHI appears in the supplied guide feature list, deriving it from the same A/N annotations would leak the target in this implementation.

No quantum-advantage claim is made.

## Reviewer path 1 — verify everything without training

```bash
python scripts/run_pipeline.py --mode verify
```

This checks the guide-source hashes, model/input artifact hashes, guide invariants, final result contracts, all notebook syntax, and repository tests. It uses no dataset and performs no training.

## Reviewer path 2 — run the actual frozen Stage06 checkpoint

The repository now bundles:

- the actual Stage04 bridge/QML checkpoints;
- the actual final Stage06 checkpoint;
- the exact frozen Stage04 QML8 and Stage05 causal16 arrays used by final Stage06;
- the frozen Stage06 reference probabilities.

Only the prepared Stage02 ECG `.npz` records remain external.

```bash
pip install -r requirements-inference.txt
python scripts/run_pipeline.py --mode inference \
  --stage02-dir /path/to/stage02_preprocessed \
  --compare-reference
```

See `docs/INFERENCE.md`.

A real end-to-end inference reproduction check was run against the frozen `x01` Stage02 record: all **522 minute rows** reproduced the stored Stage06 probabilities with maximum absolute difference `9.5367431640625e-07` on CPU, without reading official-x labels. The machine-readable receipt is `results/validation/FROZEN_STAGE06_X01_REPRODUCTION.json`.

## Reviewer path 3 — replay the frozen guide-aligned research chain

```bash
python scripts/run_pipeline.py --mode guide-replay --workspace /path/to/QML_SleepNet
```

This is accurately described as a **prepared-workspace replay**, not a raw-data one-click build. The first packaged producer depends on existing Stage02 outputs and the exact frozen label-free feature cache recorded by the Stage03 manifest. Before recomputation, the runner reproduces the notebook's cache-selection rule and **fails if today's workspace would select a different cache**. It never silently substitutes a newer experiment.

## Promoted result contract

The project-level promoted frozen fusion records:

- official-x: `35` records / `17,248` scored rows;
- accuracy: `0.9086270871985158` (90.8627%);
- balanced accuracy: `0.9076848836674374`;
- F1: `0.882475764354959`;
- MCC: `0.8084026100817799`;
- AUROC: `0.9675236374617686`;
- AUPRC: `0.9497755803318464`;
- prediction SHA-256: `063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f`.

The classical-only benchmark is slightly higher in raw official-x accuracy and is reported rather than hidden.

## Repository map

```text
QML-SleepNet/
├── guide_source/                 # exact five supplied guide screenshots
├── config/
│   ├── guide_source_manifest.json
│   ├── guide_alignment_manifest.json
│   ├── execution_manifest.json
│   └── pipeline_contract.json
├── pretrained/                   # actual frozen .pt checkpoints + hashes
├── precomputed/stage06_inputs/   # exact frozen QML8 / causal16 arrays
├── notebooks/guide/              # frozen guide-aligned producer notebooks
├── notebooks/evidence/           # canonical-QML evidence wrapper
├── notebooks/promoted_evidence/  # promoted project-level evidence
├── results/manifests/guide/      # actual guide-stage manifests
├── results/guide_stage06/        # guide-native Stage06 reference probabilities
├── scripts/
│   ├── run_pipeline.py
│   ├── run_frozen_stage06.py
│   ├── verify_artifacts.py
│   ├── check_guide_alignment.py
│   └── ...
└── docs/
    ├── GUIDE_ALIGNMENT.md
    ├── INFERENCE.md
    └── FULL_REPRODUCTION.md
```

Start with **`docs/GUIDE_ALIGNMENT.md`**. It is intentionally stricter than a marketing README.
