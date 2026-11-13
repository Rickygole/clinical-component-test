# Changelog

## v0.1.0 (2026-11-12)

First public version.

Contents:
- Module 1, `cctest agreement`: error rate among agreed answers, unanimous-wrong rate with naive, model-expectation and permutation baselines, and agreed-wrong exposure, with Wilson 95% intervals.
- Module 2, `cctest layers`: AUROC change from adding each data layer (paired bootstrap over repeats, and over patients when out-of-fold predictions are given) and each layer's solo AUROC. Decisions and flags use the patient interval when out-of-fold predictions are given.
- Shared JSON report with input file hashes, limits, decision rule and scope sentence.
- Data: `data/icdm2026` (answer letters, no question text) and `data/sgof2026` (fold AUROCs, out-of-fold predictions with anonymous ids, label-permutation null).
- `make test`: 36 known-answer and input-validation tests pass. `make reproduce`: ICDM 35 of 35 pass, SGOF 44 pass and 2 documented differences, 0 fail.
- PROTOCOL.md and PROTOCOL.pdf, NOTICE, LICENSE (MIT), CITATION.cff.

### Reproduction differences

These are reported, not tuned.

1. ICDM chance column. The paper text says the Table I chance column came from 10,000 permutations of correctness vectors. The analysis notebook actually computed a closed-form expectation: for each all-wrong question, the sum over distractors of the product of each model's wrong-letter distribution, renormalised to that question's distractors. v0.1 reports this as `model_expectation` and reproduces the paper values 3.9% and 4.2% exactly. No permutation mean or 95% interval for the chance column was computed for the paper. Two related wording points. The Table I caption says naive chance coincides closely with the empirical value. Against the closed-form expectation the paper computed, this holds approximately (1.23% against 1.41% for five models, 11.1% against 11.4% for three mid-tier models). Against the v0.1 permutation baseline, which the paper did not use, it does not (mean 3.8% for five models, ratio 6.5 rather than 19.9). Section V-A calls the 11.1% for three mid-tier models "empirical chance" although it is the naive value (closed form 11.4%, ratio 3.7, examples/reports/icdm_medqa_3midtier.json).
2. Permutation baseline redefined. Permuting correctness vectors leaves about 3 all-wrong cases per permutation at five models, so its 95th percentile is 0 and a flag would fire on any single shared error. v0.1 instead holds the observed all-wrong set fixed and permutes each model's wrong answers across all-wrong cases that share the same reference letter and option count (10,000 permutations, seed 42). The flag rule was fixed on 2026-11-12, the same day the worked examples were re-analysed, so the examples are not a prospective test of it.
3. Exposure denominators. v0.1 uses scored cases (1,271 for MedQA) while the paper used 1,273. Both print 9.2% for the three mid-tier models.
4. SGOF patient-level interval. The interval for the SGOF change from adding genotype reproduces as [-0.011, 0.013] against the paper's [-0.012, 0.012]. Stored out-of-fold probabilities were rounded to 6 decimals when saved, which creates tied scores. Pooled out-of-fold AUROC recomputed from the rounded file is 0.66531 against 0.66477 stored by the same run.
5. Genotype intervals added. v0.1 adds bootstrap intervals for the genotype GCN AUROC of 0.355: [0.322, 0.383] over repeats and [0.285, 0.415] over patients. These intervals resample fixed predictions and ignore retraining, so they are not a test against chance. The paper's [0.30, 0.69] is the label-permutation null interval, is reproduced unchanged, and remains the basis for not calling genotype worse than chance.
6. Table II gain intervals reproduce for 7 of 9 rows. The attention fusion and equal-weight fusion intervals differ by 0.001 in one bound. The reproduce script does not check these intervals.

### Other observations

- The control configuration with Flan-T5, Llama and Qwen raises the convergent_failure flag (25.5% against a 95th percentile of 14.7%); the pair of Flan-T5 and GPT-4o does not (38.5% against 39.4%). Reports for all 15 two-model MedQA pairs are in examples/reports/medqa_pairs/, and 14 of them raise the flag. See PROTOCOL.md, section 8, on specificity.
- The 22.5% figure in the ICDM paper reproduces as 117 of 520 cases with agreed answers.
- Only the genotype layer is flagged. The expression layer's patient-level lower bound is 0.526.
