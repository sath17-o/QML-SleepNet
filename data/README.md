# Data contract

Raw PhysioNet Apnea-ECG files are **not redistributed** in this repository.

For frozen Stage06 inference, supply only the prepared Stage02 directory via `--stage02-dir`. Each `{record}_preprocessed.npz` must provide:

- `ecg_filtered`
- `fs` (must be 100)
- `n_epochs`

The inference runner verifies 60-second geometry (`6000` samples per epoch) and never requests an official-x label.

For prepared-workspace guide replay, see `docs/FULL_REPRODUCTION.md`; additional Stage03 cache prerequisites are explicitly declared there.
