# Evaluation results

The principal project-level comparison on the common 17,248-row official-x evaluation set is shown below.

| System | Accuracy | Balanced accuracy | F1 | MCC | AUROC | AUPRC |
|---|---:|---:|---:|---:|---:|---:|
| Final integrated QML-inclusive system (25% physiology + 75% QML) | 0.908627 | 0.907685 | 0.882476 | 0.808403 | 0.967524 | 0.949776 |
| Physiology-only classical comparator | 0.910192 | 0.909747 | 0.884721 | 0.811954 | 0.969663 | 0.950449 |
| Reference QML system | 0.901148 | 0.900116 | 0.873093 | 0.792908 | 0.962067 | 0.942772 |

The final integrated system is the designated QML-inclusive result for the project. The physiology-only comparator has slightly higher raw accuracy on the same evaluation rows; this is reported explicitly and no quantum-advantage claim is made.

The final integrated prediction artifact contains 35 official-x records and 17,248 scored minute rows. Its prediction SHA-256 is:

`063a017e61188393bcdcdacb72958ffa3e7e0efa9432d33aa0845983462dfa1f`

Additional calibration, confusion-matrix and statistical outputs are retained in the Stage11 evaluation notebook and associated manifests.
