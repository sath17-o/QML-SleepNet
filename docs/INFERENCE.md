# Stage06 inference

The repository includes the Stage06 checkpoint and the exact Stage04-QML / Stage05-causal representation arrays consumed by that checkpoint. The source data are from the PhysioNet Apnea-ECG Database; evaluator-ready prepared Stage02 official-test records are distributed separately as integrity-checked GitHub Release assets so the Git repository itself remains compact.

## Requirements

```bash
pip install -r requirements-inference.txt
```

## Evaluator-ready data setup

Download and verify `x01`–`x35` automatically from the repository release:

```bash
python scripts/setup_evaluator_data.py --mode full
```

The setup script validates both the release-asset SHA-256 values in `config/stage02_release_manifest.json` and the individual record hashes in `data/STAGE02_OFFICIAL_X_SHA256.csv`. The verified files are extracted to `data/stage02_official_x/`.

For a quick `x01` demonstration, use:

```bash
python scripts/setup_evaluator_data.py --mode demo
```

On Windows, `RUN_DEMO.bat` and `RUN_FULL_EVALUATION.bat` automate environment setup, data preparation and inference.

## Run

```bash
python scripts/run_pipeline.py --mode inference \
  --stage02-dir data/stage02_official_x \
  --compare-reference
```

Each Stage02 record provides the prepared ECG representation expected by the published Stage06 model. The inference implementation applies the same per-record z-score normalization, ±4 SD clipping and 60-s window geometry used in the research run, aligns QML8 and causal16 by UID, reconstructs the CNN-BiLSTM/causal-gate model, and produces class-1 probabilities using the learning-OOF-selected operating threshold `0.415` unless explicitly overridden.

For official-x inference, evaluation labels are not read. A numerical reproduction receipt for record `x01` is provided in `results/validation/FROZEN_STAGE06_X01_REPRODUCTION.json`.

The bundled QML8 and causal16 arrays cover the project records represented in the published artifacts. Applying the model to an arbitrary new patient requires execution of the corresponding upstream feature, QML and causal-representation stages; this repository does not claim arbitrary raw-ECG inference from the Stage06 checkpoint alone.
