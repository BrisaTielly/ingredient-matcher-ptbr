# Evaluation report

Thresholds were calibrated on validation only; metrics below are from the frozen test split.

Bootstrap percentile intervals are stratified by match/no-match class (2,000 samples).

| Method | F1 (95% CI) | Precision | Recall | Top-1 | Recall@5 | No-match acc. | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| RapidFuzz | 0.900 [0.826, 0.959] | 0.900 | 0.900 | 0.933 | 1.000 | 0.667 | 0.909 |
| E5 base | 0.891 [0.821, 0.950] | 0.898 | 0.883 | 0.933 | 1.000 | 0.500 | 0.894 |
| E5 fine-tuned | 0.975 [0.932, 1.000] | 0.983 | 0.967 | 0.983 | 1.000 | 1.000 | 0.894 |
