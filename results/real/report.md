# Evaluation report

Thresholds were calibrated on validation only; metrics below are from the reviewed Open Prices slice.

Bootstrap percentile intervals are stratified by match/no-match class (2,000 samples).

| Method | F1 (95% CI) | Precision | Recall | Top-1 | Recall@5 | No-match acc. | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| RapidFuzz | 0.605 [0.492, 0.708] | 0.565 | 0.650 | 0.650 | 0.817 | 0.250 | 0.863 |
| E5 base | 0.818 [0.741, 0.885] | 0.750 | 0.900 | 0.900 | 1.000 | 0.400 | 0.900 |
| E5 fine-tuned | 0.874 [0.810, 0.931] | 0.881 | 0.867 | 0.950 | 1.000 | 0.700 | 0.738 |
