# Frozen Stage06 inference

The repository bundles the **actual frozen Stage06 checkpoint** and the exact frozen Stage04-QML / Stage05-causal feature arrays consumed by that checkpoint. It does **not** redistribute PhysioNet ECG records.

Required external input is therefore only the prepared Stage02 record directory:

```text
stage02_preprocessed/
├── x01_preprocessed.npz
├── x02_preprocessed.npz
├── ...
└── x35_preprocessed.npz
```

Each record must contain `ecg_filtered`, `fs`, and `n_epochs`. The runner enforces `fs=100` and `len(ecg_filtered)=n_epochs*6000`.

Run official-x inference:

```bash
python scripts/run_frozen_stage06.py \
  --stage02-dir /path/to/stage02_preprocessed \
  --split official-x \
  --compare-reference
```

The script reproduces the exact Stage06 inference preprocessing from the frozen training notebook: per-record z-score, clip ±4 SD, 60-s windows, QML8 + causal16 alignment by UID, the frozen CNN-BiLSTM/causal-gate architecture, softmax class-1 probability, and the learning-OOF-selected operating threshold `0.415` from `FINAL_OPERATING_THRESHOLD.json`.

`--compare-reference` compares the generated probabilities with `results/guide_stage06/final_predictions.npz`. It does not access official-x labels.

For a small plumbing check, add `--limit 32`; do not treat a limited run as the full reported evaluation.
