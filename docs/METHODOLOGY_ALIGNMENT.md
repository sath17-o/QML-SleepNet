# Methodology alignment and implementation scope

This document records the correspondence between the supplied methodological specification and the implemented QML-SleepNet pipeline. The five source diagrams are preserved under `guide_source/` solely as provenance records; their SHA-256 values are maintained in `config/guide_source_manifest.json`.

Where the specification is under-defined, the implementation choice is stated explicitly. Where the available labels or artifacts do not support a requested task, the repository reports the limitation rather than asserting unsupported completion.

## Implemented research sequence

```text
Apnea-ECG
  → prepared 60-s Stage02 ECG windows
  → physiological feature engineering
  → ANOVA → mRMR → SHAP → PCA128
  → neural bridge 128 → 64 → 32 → 8
  → QML evaluation (Angle-Rx / IQP, VQC, fidelity-kernel QSVC, quantum transformer)
  → causal discovery / SCM / interventions / ACE → causal16
  → QML8 + CNN-BiLSTM temporal representation + causal-aware fusion
  → binary Apnea-vs-Normal classification
  → interpretability, robustness and final statistical evaluation
```

## Stage correspondence

| Methodological requirement | Implemented treatment | Status |
|---|---|---|
| Apnea-ECG acquisition, 35 learning + 35 official-x records, ECG at 100 Hz | Prepared Stage02 records are used; raw PhysioNet files are not redistributed | Prepared-workspace prerequisite |
| 60-s preprocessing and ECG representation | Stage06 consumes `ecg_filtered` at 100 Hz with 60-s / 6000-sample geometry | Implemented from prepared Stage02 |
| Multimodal physiological feature engineering | Stage03 research output contains 419 features: 379 source features + 40 specification-gap features | Implemented |
| ANOVA → mRMR → SHAP → PCA | Fold-safe reduction to PCA128 before the neural bridge | Implemented |
| Neural pre-encoder `128→64→32→8` | Implemented and checkpointed | Implemented |
| Angle/IQP quantum encoding, VQC, kernel classifier and quantum transformer | 8-qubit implementations evaluated; VQC depth 4; fidelity-kernel QSVC; QT latent dimension 64 | Implemented with documented design choices |
| Amplitude encoding | Not established by the audited implementation | Not claimed |
| PC / FCI / NOTEARS / LiNGAM and SCM-based causal analysis | Implemented with training-fold intervention contrasts and ACE ranking | Implemented |
| QML + CNN-BiLSTM + causal fusion | QML8 + temporal512 + gated causal16 → 536→256→128→64→2 logits | Implemented |
| Apnea / Normal classification | Binary Stage06 classifier | Implemented |
| OSA / CSA / Mixed classification | Minute-level Apnea-ECG supervision used here does not provide subtype labels | Not supported by source labels |
| A/B/C grouping | Retained only as dataset record/burden categories, not apnea subtypes | Limited secondary analysis |
| Composite classification/causal/QML objective | Implemented as `0.60 classification + 0.25 causal + 0.15 upstream QML term`; the upstream QML term has no Stage06 gradient | Implemented with explicit boundary |
| AdamW, regularization and scheduling | AdamW, warmup+cosine, dropout and 50-epoch training configuration are recorded in the Stage06 manifest | Implemented |
| Five-fold record-wise evaluation | Implemented with duplicate-safe record handling | Implemented |
| LOSO evaluation | Not established as completed in the packaged research chain | Not claimed |
| Interpretability and causal visual analysis | SHAP/QML/causal evidence is preserved in the evidence notebooks and manifests | Evidence available |
| Quantum advantage | No quantum-advantage claim is made | Explicit non-claim |

## Model identities used in this repository

1. **Stage06 hybrid model** — the single QML + CNN-BiLSTM + causal checkpoint in `pretrained/stage06/qml_sleepnet_final_guide_corrected.pt`.
2. **Reference QML system** — the fixed equal-logit QML evaluation configuration represented in `notebooks/evidence/`.
3. **Final integrated system** — the later fixed 25% physiology + 75% reference-QML logit fusion used for the reported 90.8627% project-level result.

These identities are kept separate throughout the documentation and evaluation tables.

## Terminology and provenance

Some historical file names, directory names and machine-readable keys contain earlier development terminology. They are retained only where necessary to preserve artifact lineage, hash continuity and executable compatibility. Academic reporting should use the terminology defined in this document.
