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
- Decisions and flags use the patient interval when out-of-fold predictions are given, and the interval over repeat means otherwise. The report names the interval used.
- These are standard methods. No novelty is claimed for them. Both AUROC intervals resample fixed predictions and ignore retraining, so they are narrower than a label-permutation null that retrains the model. The interval over repeat means reflects split-to-split variation only and narrows as repeats are added without new patients. Neither is a test against chance.

## 4. Baselines

Three baselines are computed for the unanimous-wrong rate.

- Naive independence: for m options, (1/(m-1))^(k-1), averaged over all-wrong cases. For five models on four-option questions it is 1.23%.
- Model expectation: closed form. For each all-wrong case, take each model's distribution over its wrong letters, renormalised to that case's distractors, multiply across models, and sum over distractors. The mean over all-wrong cases is the expectation. The chance values for the two k = 4 rows of Table I in the ICDM paper with distinct frontier models (3.9% and 4.2%) were this quantity, although the paper text describes permutations of correctness vectors. The other rows report naive chance, as the caption states (CHANGELOG, difference 1).
- Permutation baseline (used for the flag): hold the observed all-wrong set fixed, and permute each model's wrong answers across all-wrong cases that share the same reference letter and option count. 10,000 permutations, seed 42. This differs from permuting correctness vectors, which leaves about 3 all-wrong cases per permutation at k = 5, so its 95th percentile is 0 and any single shared error would fire the flag.

## 5. Flags

Fixed on 2026-11-12. The worked examples below were re-analysed the same day, after the permutation baseline had been redesigned (CHANGELOG, difference 2), so these rules are not pre-specified with respect to them. A prospective test needs data that are analysed only after this version is tagged.

- convergent_failure: unanimous-wrong rate above the 95th percentile of the permutation baseline. A flag against naive independence alone is not used, because every ICDM configuration exceeds it.
- layer_not_above_chance: no solo held-out AUROC interval for the layer lies above 0.5. Wording: "held-out performance does not exceed chance". It is never worded as "below chance".
- gain_only_with_chance_level_layer: AUROC rises when a layer carrying the previous flag is added.

## 6. Decision rule

The developer records an acceptable limit, with the date, before running. For each test the interval is compared with the limit.

- Upper bound at or below the limit: supports relying on the component for this error.
- Lower bound above the limit: fails.
- Interval straddles the limit: inconclusive. For proportions the report states the denominator needed to resolve it.

When only fold AUROCs are supplied, the layer decision uses the interval over repeat means. That interval does not shrink with more patients and can be narrowed by adding repeats, so a resulting "supports reliance" is provisional until out-of-fold predictions are supplied.

Every report carries the scope sentence: results hold only for cases drawn like the labeled set and are not a clinical safety finding.

## 7. Worked examples

Illustrative limits from examples/limits_example.json (recorded 2026-11-12): agreed answer error rate 0.05, unanimous-wrong rate 0.10, AUROC loss 0.02. They are not recommendations. Reports: examples/reports/. Inputs: data/.

ICDM, MedQA, five models (llama3_8b, qwen25_7b, gemma3n_e4b, deepseek_v3, gpt4o), report icdm_medqa_5models.json.

| quantity | count | denominator | estimate | 95% interval |
| --- | --- | --- | --- | --- |
| unanimous-wrong rate | 14 | 57 | 24.6% | 15.2% to 37.1% |
| agreed answer error rate | 14 | 395 | 3.5% | 2.1% to 5.9% |
| agreed-wrong exposure | 14 | 1,271 | 1.1% | 0.7% to 1.8% |

Baselines for the unanimous-wrong rate: naive 1.23%, model expectation 1.4%, permutation mean 3.8%, permutation 95th percentile 7.0%. The observed 24.6% is above 7.0%, so convergent_failure is raised. The ratio to naive is 19.9, to the permutation mean 6.5. Decisions against the limits: unanimous-wrong rate fails (lower bound 15.2% above 10%). Agreed answer error rate is inconclusive (interval 2.1% to 5.9% straddles 5%), and the report states 862 cases with agreed answers would be needed. The MedMCQA four-model configuration (icdm_medmcqa_4models.json) gives 71 of 301 = 23.6% (19.1% to 28.7%) against a permutation 95th percentile of 6.6% and also raises the flag. The control configuration with Flan-T5, Llama and Qwen (icdm_medqa_flan_control.json) also raises it: 71 of 278 = 25.5% against a permutation 95th percentile of 14.7%. Llama and Qwen alone give 198 of 349 = 56.7% against a 95th percentile of 38.1% (medqa_pairs/llama3_8b__qwen25_7b.json). The pair of Flan-T5 and GPT-4o does not raise the flag: 40 of 104 = 38.5% against a 95th percentile of 39.4% (medqa_pairs/flan_t5_base__gpt4o.json).

SGOF, genotype layer, report sgof_genotype_layer.json. Inputs: fold_auroc.csv and oof_predictions.csv, 10 repeats by 10 folds, 111 patients.

| quantity | value | interval |
| --- | --- | --- |
| genotype alone, GCN, AUROC | 0.355 | 0.322 to 0.383 over repeats, 0.285 to 0.415 over patients (fixed predictions, not a test against chance) |
| expression alone, GCN, AUROC | 0.607 | patient interval 0.526 to 0.676 |
| naive concatenation, loss from adding genotype | 0.343 (0.675 without, 0.331 with) | 0.303 to 0.381 |
| SGOF, loss from adding genotype | 0.003 (change -0.003) | repeats -0.005 to 0.010, patients -0.013 to 0.011 |
| validation-weighted ensemble, loss | 0.007 (0.712 without, 0.706 with) | 0.002 to 0.012 |

Genotype is flagged layer_not_above_chance because no solo interval lies above 0.5. Its AUROC of 0.355 lies inside the label-permutation null (0.30 to 0.69, two-sided p = 0.13), so it is not claimed to be worse than chance. The bootstrap intervals in the table resample fixed predictions and ignore retraining. They are about a third of the width of that null and are not a test against chance. The null itself comes from single ten-fold repeats, so it is somewhat wider than a null matched to ten repeats. Expression is not flagged because its patient-level lower bound is 0.526. Under the illustrative 0.02 limit, all eight conventional fusion methods lose AUROC (by 0.032 to 0.343), seven fail and mogcn is inconclusive. SGOF supports reliance in the main run (patient interval upper bound 0.011), and so, provisionally, does the validation-weighted ensemble (upper bound 0.012, interval over repeat means only, because no out-of-fold predictions ship for it). An earlier SGOF run of the same pipeline (sgof_earlier_run) is inconclusive under the same limit: loss 0.012, interval 0.003 to 0.021. The limit was chosen by the author on the day of the analysis, so these decisions illustrate the rule and are not evidence that SGOF is safe to rely on. A simpler validation-weighted ensemble was more accurate on this cohort, so stability is not unique to SGOF.

## 8. Limits

- Exam questions are not patients. One 111-patient cohort supplies the multi-omic example.
- Models were tested in April to May 2026 and hosted models change.
- Interval coverage at small counts is limited. The 57-case denominator is an example.
- The permutation baseline does not flag a shared letter preference: if every model always picks the same wrong letter for a given correct letter, the shared answer is attributed to individual tendencies and is not flagged. The test test_shared_letter_preference_is_not_flagged documents this.
- The patient-level interval for the SGOF change (with minus without) reproduces as -0.011 to 0.013 against the paper's -0.012 to 0.012 (as a loss interval, -0.013 to 0.011), owing to rounding of stored probabilities.
- Specificity. On synthetic panels with independent errors the convergent_failure flag does not fire (test test_independent_errors_do_not_flag). On MedQA it fires for 14 of the 15 two-model pairs (examples/reports/medqa_pairs/), including four of the five pairs that contain the near-random Flan-T5 control, by small margins (for example Flan-T5 with Llama, 38.0% against 37.0%). Flan-T5 with GPT-4o is the only pair that does not fire. Some distractors therefore attract even a near-random model. A flag says that models share wrong answers beyond their individual letter habits, not that they share one reasoning failure. Read the margin between the observed rate and the 95th percentile, not only the flag. An exchangeability check in v0.1.2, planned and committed in advance (controls/negative/), measured the flag rate when shared wrong-letter choices are absent by construction: 47 of 1,400 semi-synthetic replicates (3.4%, Wilson 95% interval 2.5% to 4.4%), every configuration's rate consistent with 5% or below, as expected by construction for that null. It confirms the implementation, not specificity on real data; a control with randomised option order is still owed.
- Results are evidence for a developer's decision, not a safety certification. The decision label "supports reliance" applies only within the scope sentence.

## 9. Versioning

This is protocol v0.1. A v0.2 could add outside datasets, clustered intervals, and a mapping from free text to discrete answers. Any change to a threshold, baseline or interval method will be recorded in CHANGELOG.md with its date.
