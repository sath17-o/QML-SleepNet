# Model architecture

## Stage06 hybrid model

The implemented hybrid pathway contains:

1. physiological feature engineering and dimensionality reduction;
2. a `128 → 64 → 32 → 8` neural bridge;
3. an 8-dimensional QML representation based on the selected Angle-Rx VQC, with quantum-kernel and quantum-transformer comparators evaluated separately;
4. causal discovery, structural outcome modelling and ACE-derived causal representation;
5. a temporal Conv1D → BiLSTM → self-attention branch;
6. causal-aware fusion of the QML, temporal and causal representations.

## Reference QML evaluation system

The QML-focused reference configuration achieved **90.1148%** accuracy on the project official-x evaluation set.

## Final integrated QML-inclusive system

The final integrated configuration combines:

`25% Stage15A physiology + 75% reference QML` using fixed logit fusion.

Accuracy: **90.8627%**.

This is reported as a QML-inclusive integration, not as evidence that the physiology-only component is quantum.

## Classical comparator

The physiology-only Stage15A CatBoost + temperature scaling + HMM configuration achieved **91.0192%** accuracy on the same project evaluation rows.
