# cctest protocol, version 0.1

Fixed 2026-11-12. Applies to cctest v0.1.0.

## 1. Purpose and scope

cctest is a pre-release check for a clinical AI system built from several components. It reports, for the components a team is adding, whether a combination behaves worse than its parts suggest. It is designed to let teams check two things before deployment: whether combined language models share wrong answers, and whether an added data layer lowers held-out AUROC. It reports. It does not prescribe a fix.

v0.1 handles discrete outputs only: multiple-choice answer letters and binary labels. Free text is out of scope.

## 2. Definitions

Agreement module (unit: a case answered by k models, with m options).

- Agreed answer error rate: among cases where all k models give the same answer, the share where that answer is wrong.
- Unanimous-wrong rate: among cases all k models answered wrongly, the share where all chose the same wrong option.
- Agreed-wrong exposure: cases where all k models agree on a wrong answer, over all scored cases.
- A case is scored if every chosen model gave a valid letter. Unscored cases are counted in the report notes, never dropped silently. Duplicate (case_id, model_id) pairs and unequal model coverage reject the input.

Layers module (unit: a patient, held out in every fold).

- Solo layer AUROC: held-out AUROC of a model using one layer alone.
- AUROC loss from adding a layer: AUROC without the layer minus AUROC with it, on identical folds and repeats. Positive means the layer hurt. The signed change (with minus without) is also reported.

## 3. Intervals

- Proportions: Wilson score interval, 95%.
- AUROC, over repeats: percentile interval from 10,000 bootstrap resamples of the repeat-level means, paired across with and without, seed 2026.
- AUROC, over patients (when out-of-fold predictions are supplied): 2,000 patient resamples, AUROC averaged over repeats in each resample, seed 2026.
- These are standard methods. No novelty is claimed for them. Folds within a repeat share training patients, so the intervals are optimistic about new patients.

## 4. Baselines

Three baselines are computed for the unanimous-wrong rate.

- Naive independence: for m options, (1/(m-1))^(k-1), averaged over all-wrong cases. For five models on four-option questions it is 1.23%.
- Model expectation: closed form. For each all-wrong case, take each model's distribution over its wrong letters, renormalised to that case's distractors, multiply across models, and sum over distractors. The mean over all-wrong cases is the expectation. The chance column in Table I of the ICDM paper was this quantity, although the paper text describes permutations of correctness vectors (CHANGELOG, difference 1).
- Permutation baseline (used for the flag): hold the observed all-wrong set fixed, and permute each model's wrong answers across all-wrong cases that share the same reference letter and option count. 10,000 permutations, seed 42. This differs from permuting correctness vectors, which leaves about 3 all-wrong cases per permutation at k = 5, so its 95th percentile is 0 and any single shared error would fire the flag.

## 5. Flags

Fixed on 2026-11-12, before the v0.1 reports were generated. The worked examples below were re-analysed the same day, so they are not a prospective test of these rules.

- convergent_failure: unanimous-wrong rate above the 95th percentile of the permutation baseline. A flag against naive independence alone is not used, because every ICDM configuration exceeds it.
- layer_not_above_chance: no solo held-out AUROC interval for the layer lies above 0.5. Wording: "held-out performance does not exceed chance". It is never worded as "below chance".
- gain_only_with_chance_level_layer: AUROC rises when a layer carrying the previous flag is added.

## 6. Decision rule

The developer records an acceptable limit, with the date, before running. For each test the interval is compared with the limit.

- Upper bound at or below the limit: supports relying on the component for this error.
- Lower bound above the limit: fails.
- Interval straddles the limit: inconclusive. For proportions the report states the denominator needed to resolve it.

Every report carries the scope sentence: results hold only for cases drawn like the labeled set and are not a clinical safety finding.

## 7. Worked examples

Illustrative limits from examples/limits_example.json (recorded 2026-11-12): agreed answer error rate 0.05, unanimous-wrong rate 0.10, AUROC loss 0.02. They are not recommendations. Reports: examples/reports/. Inputs: data/.

ICDM, MedQA, five models (llama3_8b, qwen25_7b, gemma3n_e4b, deepseek_v3, gpt4o), report icdm_medqa_5models.json.

| quantity | count | denominator | estimate | 95% interval |
| --- | --- | --- | --- | --- |
| unanimous-wrong rate | 14 | 57 | 24.6% | 15.2% to 37.1% |
| agreed answer error rate | 14 | 395 | 3.5% | 2.1% to 5.9% |
| agreed-wrong exposure | 14 | 1,271 | 1.1% | 0.7% to 1.8% |

Baselines for the unanimous-wrong rate: naive 1.23%, model expectation 1.4%, permutation mean 3.8%, permutation 95th percentile 7.0%. The observed 24.6% is above 7.0%, so convergent_failure is raised. The ratio to naive is 19.9, to the permutation mean 6.5. Decisions against the limits: unanimous-wrong rate fails (lower bound 15.2% above 10%). Agreed answer error rate is inconclusive (interval 2.1% to 5.9% straddles 5%), and the report states 862 cases with agreed answers would be needed. The MedMCQA four-model configuration (icdm_medmcqa_4models.json) gives 71 of 301 = 23.6% (19.1% to 28.7%) against a permutation 95th percentile of 6.6% and also raises the flag. The Flan-T5 control configuration also raises it (unanimous 25.5% against a permutation mean of 11.6%).

SGOF, genotype layer, report sgof_genotype_layer.json. Inputs: fold_auroc.csv and oof_predictions.csv, 10 repeats by 10 folds, 111 patients.

| quantity | value | interval |
| --- | --- | --- |
| genotype alone, GCN, AUROC | 0.355 | 0.322 to 0.383 over repeats, 0.285 to 0.415 over patients |
| expression alone, GCN, AUROC | 0.607 | patient interval 0.526 to 0.676 |
| naive concatenation, loss from adding genotype | 0.343 (0.675 without, 0.331 with) | 0.303 to 0.381 |
| SGOF, loss from adding genotype | 0.003 (change -0.003) | repeats -0.005 to 0.010, patients -0.013 to 0.011 |
| validation-weighted ensemble, loss | 0.007 (0.712 without, 0.706 with) | 0.002 to 0.012 |

Genotype is flagged layer_not_above_chance, because its solo intervals lie below 0.5. The interval 0.30 to 0.69 reproduced from the SGOF paper alongside the genotype AUROC is the label-permutation null, not an interval for the AUROC. Expression is not flagged because its patient-level lower bound is 0.526. Under the illustrative 0.02 limit, all eight conventional fusion methods lose AUROC (by 0.032 to 0.343), seven fail and mogcn is inconclusive. SGOF supports reliance, and so does the validation-weighted ensemble. A simpler validation-weighted ensemble was more accurate on this cohort, so stability is not unique to SGOF.

## 8. Limits

- Exam questions are not patients. One 111-patient cohort supplies the multi-omic example.
- Models were tested in April to May 2026 and hosted models change.
- Interval coverage at small counts is limited. The 57-case denominator is an example.
- The permutation baseline does not flag a shared letter preference: if every model always picks the same wrong letter for a given correct letter, the shared answer is attributed to individual tendencies and is not flagged. The test test_shared_letter_preference_is_not_flagged documents this.
- The patient-level SGOF interval reproduces as -0.011 to 0.013 against the paper's -0.012 to 0.012, owing to rounding of stored probabilities.
- Results are evidence for a developer's decision, not a safety certification.

## 9. Versioning

This is protocol v0.1. A v0.2 could add outside datasets, clustered intervals, and a mapping from free text to discrete answers. Any change to a threshold, baseline or interval method will be recorded in CHANGELOG.md with its date.
