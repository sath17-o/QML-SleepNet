# Architecture

## Final guide-primary QML parent

The frozen guide chain contains:

1. physiological feature engineering and dimensionality reduction;
2. `128 → 64 → 32 → 8` bridge;
3. quantum branch with the frozen Angle-Rx VQC representation and audited quantum comparators;
4. causal discovery / SCM / ACE-derived causal representation;
5. temporal Conv1D → BiLSTM → self-attention branch;
6. causal-aware final fusion.

The canonical guide-primary QML system achieved **90.1148%** on the historical official-x benchmark.

## Final designated QML-inclusive system

Stage 11 designates:

`25% Stage15A physiology + 75% guide-primary QML` using fixed logit fusion.

Accuracy: **90.8627%**

This is a QML-inclusive extension, not a claim that the classical parent is quantum.

## Classical comparator

The best classical-only benchmark is:

`Stage15A physiology CatBoost + temperature + HMM`

Accuracy: **91.0192%**.
