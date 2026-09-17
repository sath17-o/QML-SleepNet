# Repository submission checklist

Before sharing the repository:

- [ ] `python scripts/run_pipeline.py --mode verify` completes successfully.
- [ ] The five source diagrams remain byte-identical to `config/guide_source_manifest.json`.
- [ ] `pretrained/ARTIFACT_MANIFEST.json` verifies all bundled model and representation artifacts.
- [ ] `docs/METHODOLOGY_ALIGNMENT.md` remains available and the stated methodological limitations are preserved.
- [ ] Official-x labels and third-party raw dataset files are not added to the repository.
- [ ] OSA/CSA/Mixed is not described as a trained prediction target.
- [ ] A/B/C record categories are not interpreted as apnea subtypes.
- [ ] The 90.8627% final integrated system is not described as identical to the single Stage06 checkpoint.
- [ ] No quantum-advantage claim is made.
- [ ] The methodology replay is not described as raw-data end-to-end reproduction unless an independently verified raw→Stage02 producer is added.
