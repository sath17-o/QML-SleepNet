# Guide alignment — source-locked audit

This document is the repository's scientific alignment contract. The **five supplied guide screenshots in `guide_source/` are the authority**. Their SHA-256 hashes are frozen in `config/guide_source_manifest.json`. The implementation is not allowed to silently reinterpret a guide item just to make the repository look complete.

## Guide-native chain

```text
Apnea-ECG acquisition / annotations
        ↓
Stage02 signal preprocessing + 60-s windows
        ↓
Stage03 physiological/multimodal feature bank
        ↓
ANOVA → mRMR → SHAP → PCA (~128-D)
        ↓
classical pre-encoder 128 → 64 → 32 → 8
        ↓
Stage04 QML: Angle/IQP → VQC + fidelity kernel/QSVC + quantum transformer evidence
        ↓
Stage05 causal discovery / SCM / interventions / ACE → causal16
        ↓
Stage06: QML8 + CNN-BiLSTM temporal512 + gated causal16
        ↓
536 → 256 → 128 → 64 → 2 logits (Task A: Apnea vs Normal)
        ↓
Stage07 interpretability / Stage08 training protocol / Stage09 evaluation / Stage10 outputs
```

## Exact implementation / deviation matrix

| Guide item | Frozen implementation | Status |
|---|---|---|
| Apnea-ECG, 35 learn + 35 official-x | The project uses the guide's Apnea-ECG split. Raw PhysioNet files are not redistributed. | Prepared-workspace prerequisite |
| Stage02 preprocessing | Final Stage06 consumes `ecg_filtered`, `fs=100`, `n_epochs`, 60-s/6000-sample geometry. A verified raw→Stage02 producer is **not** packaged in the frozen chain. | Not claimed as raw one-click |
| Stage03 multimodal features | Frozen Stage03 rebuild: 379-feature label-free cache + 40 guide-gap features = 419. | Implemented |
| AHI in feature list | **Not used as input.** In this dataset, deriving AHI from the same A/N labels would leak the target. | Leakage-safe adaptation |
| ANOVA→mRMR→SHAP→PCA | Fold-safe Stage04 bridge selection; PCA to 128-D before MLP. | Implemented |
| Pre-encoder 128→64→32→8 | Checkpoint and audited Stage04 manifest lock this geometry. | Implemented |
| Angle / IQP encodings | Angle-Rx and dense all-pairs IQP are audited. | Implemented |
| Amplitude encoding | Not established by the audited frozen core. | **Not claimed** |
| 6–8 qubits / VQC | 8 qubits; depth 4; 96 quantum parameters; StronglyEntanglingLayers; CNOT; Rz–Ry–Rz; Pauli-Z expectations. | Implemented |
| Fidelity kernel / QSVC | Fidelity kernel with SVM/QSVM comparison. | Implemented |
| Quantum transformer | Frozen Angle/IQP QT checkpoints; latent dimension 64. | Implemented with documented instantiation |
| PC / FCI / NOTEARS / LiNGAM | All four appear in the audited Stage05 causal core. | Implemented |
| SCM / interventions / ACE | Structural logistic outcome SCM, Q25/Q75 interventions, ACE ranking; causal16 chosen from training-fold evidence. | Implemented |
| Causal-aware fusion | Stage06 gates causal16; QML8 is preserved unchanged. | Implemented with documented minimal choice |
| CNN-BiLSTM | Conv1D64 k=3/5/7 → BN/ReLU/MaxPool → BiLSTM128×2 → self-attention → avg+max = temporal512. | Implemented |
| Guide Task A: Apnea/Normal | Final Stage06 is a 2-logit binary classifier. | Implemented |
| Guide Task B: OSA/CSA/Mixed | Apnea-ECG minute supervision does not provide this target. | **Not supported / not claimed** |
| Guide Task C: A/B/C | A/B/C can be described only as dataset record/burden categories in this project, not OSA/CSA/Mixed subtypes. | Limited secondary analysis |
| Composite loss | `0.60 classification + 0.25 causal + 0.15 frozen upstream QML term`; the frozen QML term has zero Stage06 gradient rather than inventing a surrogate. | Implemented with scientific boundary |
| AdamW / warmup + cosine / regularization | Frozen Stage06 manifest locks the concrete settings. | Implemented |
| 5-fold CV | Duplicate-safe learning-record CV, with official-x labels sealed. | Implemented |
| LOSO | Listed by guide, but not established as completed by this packaged core. | **Not claimed** |
| XAI / robustness / statistics | Evidence notebooks/manifests are included with their scope boundaries. | Evidence layer |
| Quantum advantage | The guide asks for quantum comparison metrics; the project does **not** claim quantum advantage. | Explicit non-claim |

## System identity boundary

Three related objects must not be conflated:

1. **Guide-native Stage06 checkpoint** — `pretrained/stage06/qml_sleepnet_final_guide_corrected.pt`.
2. **Canonical reported QML system** — the fixed equal-logit project evaluation wrapper in `notebooks/evidence/`; this is not merely the single Stage06 checkpoint.
3. **Promoted 90.8627% system** — a later fixed 25% Stage15A physiology + 75% canonical-QML logit fusion. It is a project-level extension, not a box drawn in the supplied guide screenshots.

This separation is intentional: reviewer convenience must not override scientific provenance.
