# Results

| system                        | role                                                                                 | quantum_in_final_function   |   physiology_logit_weight |   qml_logit_weight |     n |   accuracy |   balanced_accuracy |   precision |   sensitivity |   specificity |       f1 |      mcc |    auroc |    auprc |     brier |      nll |   tn |   fp |   fn |   tp |
|:------------------------------|:-------------------------------------------------------------------------------------|:----------------------------|--------------------------:|-------------------:|------:|-----------:|--------------------:|------------:|--------------:|--------------:|---------:|---------:|---------:|---------:|----------:|---------:|-----:|-----:|-----:|-----:|
| FINAL_QML_INCLUSIVE_PROMOTED  | Final metric-first QML-inclusive system; development-promoted before fused x scoring | True                        |                      0.25 |               0.75 | 17248 |   0.908627 |            0.907685 |    0.862159 |      0.903773 |      0.911597 | 0.882476 | 0.808403 | 0.967524 | 0.949776 | 0.0796448 | 0.433467 | 9755 |  946 |  630 | 5917 |
| STAGE15A_PHYSIOLOGY_CLASSICAL | Best classical-only historical benchmark                                             | False                       |                      1    |               0    | 17248 |   0.910192 |            0.909747 |    0.8627   |      0.907897 |      0.911597 | 0.884721 | 0.811954 | 0.969663 | 0.950449 | 0.0795853 | 0.441768 | 9755 |  946 |  603 | 5944 |
| CANONICAL_GUIDE_QML           | Canonical guide-primary QML architecture                                             | True                        |                      0    |               1    | 17248 |   0.901148 |            0.900116 |    0.851481 |      0.89583  |      0.904401 | 0.873093 | 0.792908 | 0.962067 | 0.942772 | 0.0861429 | 0.487634 | 9678 | 1023 |  682 | 5865 |

## Authoritative final system

- Name: `FIXED_LOGIT_PHYS_25_QML_75`
- Accuracy: **90.8627%**
- Balanced accuracy: **90.7685%**
- Precision: **86.2159%**
- Sensitivity: **90.3773%**
- Specificity: **91.1597%**
- F1: **88.2476%**
- MCC: **0.8084**
- AUROC: **96.7524%**
- AUPRC: **94.9776%**
