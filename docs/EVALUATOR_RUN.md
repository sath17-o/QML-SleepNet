# Evaluator execution guide

This guide provides the shortest reproducible path for executing QML-SleepNet on an independent machine.

## Windows quick demonstration

Prerequisite: Python 3.11 with the Windows `py` launcher and an internet connection for dependency installation if the local virtual environment is not already prepared.

From the repository root:

```bat
RUN_DEMO.bat
```

The script performs the following operations automatically:

1. creates `.venv` with Python 3.11 when it is not already present;
2. installs `requirements-inference.txt` when NumPy/PyTorch are not already available in that environment;
3. verifies the bundled `data/stage02_official_x/x01_preprocessed.npz` file against the recorded byte count and SHA-256 value;
4. runs the published Stage06 checkpoint on `x01` using CPU inference; and
5. compares the recomputed probabilities with the stored Stage06 reference probabilities.

The successful terminal condition is:

```text
REFERENCE COMPARISON PASS
DEMO PASS: x01 reproduced the stored Stage06 probabilities.
```

Small machine-dependent floating-point differences are permitted up to the inference script's published tolerance (`1e-4`).

## Complete 35-record Stage06 reproduction

On Windows:

```bat
RUN_FULL_EVALUATION.bat
```

The script verifies all 35 prepared Stage02 records bundled under `data/stage02_official_x/` against `data/STAGE02_OFFICIAL_X_SHA256.csv` and then runs the complete official-x Stage06 reference comparison. Official-x labels are not read by the inference path.

The successful terminal condition is:

```text
REFERENCE COMPARISON PASS
FULL EVALUATION PASS: all official-x reference probabilities reproduced within tolerance.
```

## Cross-platform manual commands

On Linux/macOS, or when a manual workflow is preferred:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-inference.txt
.venv/bin/python scripts/setup_evaluator_data.py --mode demo
.venv/bin/python scripts/run_pipeline.py --mode inference \
  --stage02-dir data/stage02_official_x \
  --records x01 \
  --device cpu \
  --compare-reference
```

For all 35 records, replace `--mode demo` with `--mode full` and omit `--records x01`.

## Data integrity and provenance

The prepared Stage02 files correspond to the `x01`–`x35` official test recordings of the PhysioNet Apnea-ECG Database v1.0.0. The original source is:

- PhysioNet Apnea-ECG Database v1.0.0: https://physionet.org/content/apnea-ecg/1.0.0/
- DOI: `10.13026/C23W2R`
- file license: Open Data Commons Attribution License v1.0

The prepared ECG representations used by the published Stage06 model are versioned directly in the repository. Their integrity is fixed by `data/STAGE02_OFFICIAL_X_SHA256.csv`.

## What this test demonstrates

The Stage06 evaluator path loads the published PyTorch checkpoint, the versioned QML8 and causal16 representations, and the prepared Stage02 ECG input; reconstructs the CNN-BiLSTM/causal-gate architecture; computes probabilities; and numerically compares those probabilities with the stored research reference.

It is an executable inference-reproduction test. It is distinct from re-training the complete research pipeline and from the later project-level final integrated evaluation configuration described elsewhere in the repository.
