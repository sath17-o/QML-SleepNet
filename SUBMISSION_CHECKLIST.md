# Submission checklist

Before publishing this repository:

- [ ] `python scripts/run_pipeline.py --mode verify` passes.
- [ ] The five files under `guide_source/` remain byte-identical to `config/guide_source_manifest.json`.
- [ ] `pretrained/ARTIFACT_MANIFEST.json` hashes all bundled frozen checkpoints/arrays successfully.
- [ ] `docs/GUIDE_ALIGNMENT.md` remains in the root reviewer path; do not remove the non-claims.
- [ ] Do not add official-x labels or raw third-party dataset files.
- [ ] Do not describe OSA/CSA/Mixed as a trained target.
- [ ] Do not describe A/B/C record categories as OSA/CSA/Mixed subtypes.
- [ ] Do not describe the promoted 90.8627% fusion as the single Stage06 checkpoint.
- [ ] Do not claim quantum advantage.
- [ ] Do not call `guide-replay` a raw-from-scratch pipeline unless a verified raw→Stage02 producer is later added and audited.
