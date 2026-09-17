# Data requirements

Raw PhysioNet records are not redistributed in this repository.

For Stage06 inference, provide the prepared Stage02 directory using `--stage02-dir`. Each `{record}_preprocessed.npz` must contain the fields expected by the published Stage06 inference script, including the filtered ECG representation and minute geometry.

For prepared-workspace methodology replay, see `docs/FULL_REPRODUCTION.md`. Stage03 source-cache prerequisites are declared explicitly there.
