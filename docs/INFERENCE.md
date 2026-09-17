# Stage06 inference

The repository includes the Stage06 checkpoint, the exact Stage04-QML / Stage05-causal representation arrays consumed by that checkpoint, and the prepared Stage02 official-test records required for executable evaluator reproduction.

## Requirements

```bash
pip install -r requirements-inference.txt
```

## Evaluator-ready data verification

The prepared `x01`–`x35` Stage02 records are versioned directly under `data/stage02_official_x/`.

Verify all 35 files against the repository checksum manifest:

```bash
python scripts/setup_evaluator_data.py --mode full
```

For a quick `x01` integrity check:

```bash
python scripts/setup_evaluator_data.py --mode demo
```

The verifier checks the individual record byte counts and SHA-256 values in `data/STAGE02_OFFICIAL_X_SHA256.csv`. It does not download data.

On Windows, `RUN_DEMO.bat` and `RUN_FULL_EVALUATION.bat` automate environment setup, data verification and inference.

## Run

```bash
python scripts/run_pipeline.py --mode inference \
  --stage02-dir data/stage02_official_x \
  --compare-reference
```

Each Stage02 record provides the prepared ECG representation expected by the published Stage06 model. The inference implementation applies the same per-record z-score normalization, ±4 SD clipping and 60-s window geometry used in the research run, aligns QML8 and causal16 by UID, reconstructs the CNN-BiLSTM/causal-gate model, and produces class-1 probabilities using the learning-OOF-selected operating threshold `0.415` unless explicitly overridden.

For official-x inference, evaluation labels are not read. A numerical reproduction receipt for record `x01` is provided in `results/validation/FROZEN_STAGE06_X01_REPRODUCTION.json`.

The bundled QML8 and causal16 arrays cover the project records represented in the published artifacts. Applying the model to an arbitrary new patient requires execution of the corresponding upstream feature, QML and causal-representation stages; this repository does not claim arbitrary raw-ECG inference from the Stage06 checkpoint alone.
