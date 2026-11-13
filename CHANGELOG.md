# Changelog

## v0.1.0 (unreleased, built 2026-11-12)

First public version.

Contents:
- Module 1, `cctest agreement`: error rate among agreed answers, unanimous-wrong rate with naive, model-expectation and permutation baselines, and agreed-wrong exposure, with Wilson 95% intervals.
- Module 2, `cctest layers`: AUROC change from adding each data layer (paired bootstrap over repeats, and over patients when out-of-fold predictions are given) and each layer's solo AUROC.
- Shared JSON report with input file hashes, limits, decision rule and scope sentence.
- Data: `data/icdm2026` (answer letters, no question text) and `data/sgof2026` (fold AUROCs, out-of-fold predictions with anonymous ids, label-permutation null).
- `make test`: 35 known-answer and input-validation tests pass. `make reproduce`: ICDM 35 of 35 pass, SGOF 44 pass and 2 documented differences, 0 fail.
- PROTOCOL.md and PROTOCOL.pdf, NOTICE, LICENSE (MIT), CITATION.cff.

The date-released field in CITATION.cff (2026-11-12) is the build date and is to be updated at tagging.

### Reproduction differences

These are reported, not tuned.

1. ICDM chance column. The paper text says the Table I chance column came from 10,000 permutations of correctness vectors. The analysis notebook actually computed a closed-form expectation: for each all-wrong question, the sum over distractors of the product of each model's wrong-letter distribution, renormalised to that question's distractors. v0.1 reports this as `model_expectation` and reproduces the paper values 3.9% and 4.2% exactly.
2. Permutation baseline redefined. Permuting correctness vectors leaves about 3 all-wrong cases per permutation at five models, so its 95th percentile is 0 and a flag would fire on any single shared error. v0.1 instead holds the observed all-wrong set fixed and permutes each model's wrong answers across all-wrong cases that share the same reference letter and option count (10,000 permutations, seed 42). The flag rule was fixed on 2026-11-12, the same day the worked examples were re-analysed, so the examples are not a prospective test of it.
5. Exposure denominators. v0.1 uses scored cases (1,271 for MedQA) while the paper used 1,273. Both print 9.2% for the three mid-tier models.
6. SGOF patient-level interval. The interval for the SGOF change from adding genotype reproduces as [-0.011, 0.013] against the paper's [-0.012, 0.012]. Stored out-of-fold probabilities were rounded to 6 decimals when saved, which creates tied scores. Pooled out-of-fold AUROC recomputed from the rounded file is 0.66531 against 0.66477 stored by the same run.
7. Genotype intervals added. v0.1 adds bootstrap intervals for the genotype GCN AUROC of 0.355: [0.322, 0.383] over repeats and [0.285, 0.415] over patients. The paper's [0.30, 0.69] is the label-permutation null interval and is reproduced unchanged.
8. Table II gain intervals reproduce for 7 of 9 rows. The attention fusion and equal-weight fusion intervals differ by 0.001 in one bound. The reproduce script does not check these intervals.

The numbering follows the build notes. Items 3, 4, 9 and 10 there are not reproduction differences. The Flan-T5 control configuration also raises the flag (unanimous 25.5% against a permutation mean of 11.6%).
