# Reproducibility checklist

Use this checklist before sharing or archiving a release of QML-SleepNet.

## Repository verification

- [ ] `python scripts/run_pipeline.py --mode verify` completes successfully.
- [ ] GitHub Actions `Verify reproducibility package` is passing on the commit being shared.
- [ ] The five source diagrams remain byte-identical to `config/guide_source_manifest.json`.
- [ ] `pretrained/ARTIFACT_MANIFEST.json` verifies all bundled model and representation artifacts.
- [ ] `docs/METHODOLOGY_ALIGNMENT.md` remains available and the stated methodological limitations are preserved.

## Evaluator execution

- [ ] `RUN_DEMO.bat` reproduces the stored Stage06 probabilities for `x01` within the documented tolerance.
- [ ] `RUN_FULL_EVALUATION.bat` verifies all 35 prepared Stage02 records and reproduces all `17,248` Stage06 reference probabilities within tolerance.
- [ ] `RUN_FINAL_INTEGRATED_EVALUATION.bat` reproduces the fixed 25% physiology + 75% QML weighted-logit evaluation and ends with `FINAL INTEGRATED EVALUATION PASS`.
- [ ] The final integrated replay still reproduces the published metric contract and confusion matrix in `config/final_integrated_execution_manifest.json`.

## Data and label boundaries

- [ ] Raw third-party PhysioNet source recordings are not presented as repository-generated data.
- [ ] The bundled `data/stage02_official_x/` files are described as project-prepared derivatives and remain fixed by `data/STAGE02_OFFICIAL_X_SHA256.csv`.
- [ ] The scoring-only `precomputed/final_integrated_inputs/OFFICIAL_X_EVALUATION_LABELS.csv` remains restricted to final evaluation replay and is loaded only after the fused predictions are fixed.
- [ ] Official-x labels are not read by the Stage06 inference path.

## Reporting boundaries

- [ ] OSA / CSA / Mixed is not described as a trained prediction target.
- [ ] A/B/C record categories are not interpreted as apnea subtypes.
- [ ] AHI is not described as a model input.
- [ ] The 90.8627% result is attributed to the final integrated 25% physiology + 75% QML configuration, not to the single Stage06 checkpoint.
- [ ] No quantum-advantage claim is made.
- [ ] The final integrated replay is described as an evaluation replay from versioned parent predictions, not as parent-model retraining.
- [ ] The methodology replay is not described as raw-data end-to-end reproduction unless an independently verified raw-to-Stage02 producer is added.

The purpose of this checklist is to keep the repository's public claims aligned with its executable evidence.