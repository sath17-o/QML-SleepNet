# Reproduction modes

The repository separates four reproducibility tasks: **repository verification**, **Stage06 inference**, **prepared-workspace methodology replay**, and **final-system evidence replay**.

## 1. Repository verification — no dataset and no training

```bash
python scripts/run_pipeline.py --mode verify
```

This checks source-diagram hashes, model/input artifact hashes, methodological invariants, headline result contracts, notebook syntax and repository tests.

## 2. Stage06 inference

```bash
python scripts/run_pipeline.py --mode inference --stage02-dir /path/to/stage02_preprocessed --compare-reference
```

The Stage06 model, Stage04 QML8 representation and Stage05 causal16 representation are included. Only prepared Stage02 ECG records are external.

## 3. Prepared-workspace methodology replay

```bash
python scripts/run_pipeline.py --mode methodology-replay --workspace /path/to/QML_SleepNet
```

The replay executes the research notebooks in dependency order and verifies each declared output contract. It is not described as raw-data end-to-end reproduction because the Stage03 rebuild requires:

- `data/processed/stage02_preprocessed/`; and
- the exact label-free feature-cache directory recorded by the Stage03 research manifest (`15A_feature_bank_v1_4_1/...` for the published run).

The Stage03 notebook searches multiple cache roots. Before execution, the runner reproduces that selection rule and stops if the current workspace would select a different cache. This prevents unintentional substitution of a different experimental source state.

No independently verified raw-PhysioNet→Stage02 producer is included in this repository. The runner modifies only temporary notebook copies to replace the Colab project-root path and remove Drive-mount/package-install cells; the scientific notebook code is otherwise unchanged.

## 4. Final-system evidence replay

```bash
python scripts/run_pipeline.py --mode final-evidence --workspace /path/to/QML_SleepNet
```

This reconstructs the later 25% physiology + 75% reference-QML integration evidence when its parent artifacts are present. It is distinct from Stage06 model training.

`--mode full` runs the prepared-workspace methodology replay followed by the final-system evidence replay. It does not imply raw-data one-click reproduction.
