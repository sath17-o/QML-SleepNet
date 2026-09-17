# Model and representation artifacts

This directory contains the versioned checkpoint files used by the published research implementation. `ARTIFACT_MANIFEST.json` records byte size, SHA-256 and workspace provenance for every bundled artifact.

Included checkpoints:

- `bridge/bridge128to8_model.pt` — Stage04 neural bridge (`128→64→32→8`).
- `qml/final_vqc_angle_rx.pt` — Stage04 Angle-Rx VQC checkpoint.
- `qml/final_vqc_iqp_dense.pt` — Stage04 dense-IQP VQC checkpoint.
- `qml/final_qt_angle_rx.pt` — Stage04 Angle-Rx quantum-transformer checkpoint.
- `qml/final_qt_iqp_dense.pt` — Stage04 dense-IQP quantum-transformer checkpoint.
- `stage06/qml_sleepnet_final_guide_corrected.pt` — Stage06 binary Apnea-vs-Normal CNN-BiLSTM + QML8 + causal16 checkpoint.

The final 90.8627% QML-inclusive result is a fixed project-level fusion of component predictions rather than a separate monolithic `.pt` checkpoint. See `docs/METHODOLOGY_ALIGNMENT.md`.
