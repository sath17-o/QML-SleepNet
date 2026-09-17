# Data availability and provenance

QML-SleepNet uses the **PhysioNet Apnea-ECG Database v1.0.0**. The source dataset contains 70 records, including a 35-record learning set and a 35-record official test set (`x01` through `x35`). The source dataset is distributed by PhysioNet under the **Open Data Commons Attribution License v1.0**.

Source: https://physionet.org/content/apnea-ecg/1.0.0/

DOI: `10.13026/C23W2R`

Original Apnea-ECG publication: T. Penzel, G. B. Moody, R. G. Mark, A. L. Goldberger, and J. H. Peter, “The Apnea-ECG Database,” *Computers in Cardiology*, vol. 27, pp. 255–258, 2000.

## Evaluator-ready prepared Stage02 records

The prepared Stage02 `x01`–`x35` records used for executable Stage06 inference reproduction are versioned directly under:

```text
data/stage02_official_x/
```

Per-record byte counts and SHA-256 values are recorded in `data/STAGE02_OFFICIAL_X_SHA256.csv`.

Evaluators do not need Google Drive, Git LFS or a separate release download. On Windows:

```bat
RUN_DEMO.bat
```

verifies and reproduces `x01`. For the complete 35-record reference comparison:

```bat
RUN_FULL_EVALUATION.bat
```

Both entry points fail closed if the required prepared data are missing or do not match the recorded hashes.

## Manual Stage06 input

A manually supplied Stage02 directory may still be passed using `--stage02-dir`. Each `{record}_preprocessed.npz` must contain the filtered ECG representation and minute geometry expected by the published Stage06 inference script.

For prepared-workspace methodology replay, see `docs/FULL_REPRODUCTION.md`. Stage03 source-cache prerequisites are declared explicitly there.
