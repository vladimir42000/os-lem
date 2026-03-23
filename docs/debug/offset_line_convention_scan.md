# Debug offset-line contribution convention scan

Purpose:
- hold solver math fixed
- test whether the remaining offset-line driver/mouth mismatch against Hornresp is
  best explained by contribution mapping or polarity convention rather than TL-core
  physics

Current branch intent:
- start from `fix/v0.2.0-radiator-observation-topology-aware-source`
- add only a debug scanner
- do not edit kernel equations in this patch

Interpretation rule:
- if a direct-mapping variant wins clearly, keep `front_rad -> driver` and
  `mouth_rad -> port`, then inspect sign or phase-reference handling
- if a swapped variant wins clearly, fix the comparison labeling/mapping first
- if no variant wins clearly, escalate to Hornresp contribution export semantics
