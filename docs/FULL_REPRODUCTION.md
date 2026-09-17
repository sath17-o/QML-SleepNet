# Reproduction modes and what they mean

The repository deliberately distinguishes **verification**, **frozen inference**, **prepared-workspace guide replay**, and **project-level promoted evidence**.

## 1. Frozen verification — no dataset, no training

```bash
python scripts/run_pipeline.py --mode verify
```

Checks guide-image hashes, frozen-artifact hashes, guide-alignment invariants, headline result contracts, notebook syntax, and repository tests.

## 2. Frozen guide-native Stage06 inference

```bash
python scripts/run_pipeline.py --mode inference --stage02-dir /path/to/stage02_preprocessed --compare-reference
```

The Stage06 model + Stage04 QML8 + Stage05 causal16 are bundled. Only Stage02 preprocessed ECG records are external.

## 3. Prepared-workspace guide replay

```bash
python scripts/run_pipeline.py --mode guide-replay --workspace /path/to/QML_SleepNet
```

This executes the frozen scientific notebooks in dependency order and checks each output manifest. It is **not called raw-from-scratch reproduction** because the Stage03 rebuild requires:

- `data/processed/stage02_preprocessed/`
- the exact frozen label-free feature-cache directory recorded in `STAGE03_GUIDE_REBUILD_MANIFEST.json` (`15A_feature_bank_v1_4_1/...` in the frozen run). The notebook can search several cache roots; the runner preflights that search and refuses recomputation if the current workspace would select a different cache.

No verified standalone raw-PhysioNet→Stage02 producer is packaged in this frozen chain, so the repository states that limitation instead of hiding it.

The runner edits only temporary notebook copies to replace the Colab project-root path and remove Drive-mount / notebook package-install lines. It fails closed on missing prerequisites.

## 4. Project-level promoted evidence replay

```bash
python scripts/run_pipeline.py --mode promoted-evidence --workspace /path/to/QML_SleepNet
```

This is separate from guide-native model training. It reconstructs evidence for the later frozen 25% physiology + 75% canonical-QML promoted fusion when its parent artifacts are present.

`--mode full` means **prepared-workspace guide replay + promoted evidence replay**. It does not mean raw-data one-click reproduction.
