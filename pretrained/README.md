# Frozen checkpoints

These are the actual frozen checkpoint files copied from the project workspace. `ARTIFACT_MANIFEST.json` records byte size, SHA-256 and provenance path for every bundled artifact.

- `bridge/bridge128to8_model.pt` — Stage04 classical bridge, 128→64→32→8.
- `qml/final_vqc_angle_rx.pt` — Stage04 Angle-Rx VQC.
- `qml/final_vqc_iqp_dense.pt` — Stage04 dense-IQP VQC.
- `qml/final_qt_angle_rx.pt` — Stage04 Angle-Rx quantum-transformer checkpoint.
- `qml/final_qt_iqp_dense.pt` — Stage04 dense-IQP quantum-transformer checkpoint.
- `stage06/qml_sleepnet_final_guide_corrected.pt` — final **guide-native Task-A binary** CNN-BiLSTM + QML8 + causal16 checkpoint.

The promoted 90.8627% system is not a separate monolithic `.pt`; it is a fixed project-level fusion of frozen parent predictions. See `docs/GUIDE_ALIGNMENT.md`.
