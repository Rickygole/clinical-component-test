# Negative control for v0.1.2: results

## Timeline

The plan (PLAN_v0.1.2.md) and the generator (make_null.py) were committed as abea6c85bdb7d4c90875fb88354c41150872c529 at 2026-11-12 22:57:44 US Eastern time, which is 2026-11-13 03:57:44 UTC, and pushed immediately afterwards (the push returned `9faf3c0..abea6c8  main -> main` at about 03:57:45 UTC). No replicate dataset was generated and the agreement test was not run on any semi-synthetic data before that commit. The only earlier execution of the script was on a 300-question toy file of uniformly random answers, to check that it runs; that output was discarded. The full run started at 03:57:50 UTC and had written both result files by 04:05 UTC, about 7 minutes with 8 worker processes on a machine that was heavily loaded by other work (load average near 80). Nothing was committed between the plan commit and the end of the run; these results were committed afterwards, in commit d1427f7. The plan, the generator, R, the seeds and the decision statement were not changed after the results were seen.

## What was run

The unchanged v0.1.0 command line (`cctest agreement <csv> --models <list>`, 10,000 permutations, seed 42, no limits file) on 7 configurations. For each configuration, one run on the real data (replicate 0) and 200 runs on semi-synthetic null replicates (1,400 in all). In a replicate, every model keeps its real per-question correctness exactly, and each wrong answer is replaced by an independent draw from that model's own wrong-letter distribution restricted to that question's distractors. The all-wrong set is therefore identical in every replicate of a configuration, and equal to the real one (all-wrong counts 279, 143, 73, 57, 301, 104 and 41, the same as in the real runs). The generator asserted preservation of correctness, validity and option range for every replicate. Commands: COMMANDS.md. Per-replicate results: replicates_v0.1.2.tsv; real-data rows: real_data_v0.1.2.tsv; one example report per configuration, for replicate 1 and for the real data: examples/.

The real-data rows reproduce the earlier results (for example HELM panel A 20 of 104 and panel B 20 of 41 unanimous-wrong, with permutation 95th percentiles of 6.7% and 7.3%).

## Results

Flag rate = replicates in which convergent_failure was raised, out of 200, with a Wilson 95% interval.

| configuration | null flag rate | Wilson 95% interval | real-data flag | real unanimous-wrong rate | real permutation 95th percentile | null mean unanimous-wrong rate | null maximum | as specified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MedQA 3, mid-tier (medqa3_mid) | 3 of 200 = 1.5% | 0.5% to 4.3% | 1 | 117 of 279 = 41.9% | 15.1% | 11.4% | 16.1% | yes, below 5% |
| MedQA 4, + DeepSeek-V3 (medqa4_deepseek) | 8 of 200 = 4.0% | 2.0% to 7.7% | 1 | 48 of 143 = 33.6% | 7.0% | 3.9% | 9.8% | yes, includes 5% |
| MedQA 4, + GPT-4o (medqa4_gpt4o) | 9 of 200 = 4.5% | 2.4% to 8.3% | 1 | 19 of 73 = 26.0% | 11.0% | 4.3% | 12.3% | yes, includes 5% |
| MedQA 5, mid-tier + DeepSeek-V3 + GPT-4o (medqa5_all) | 3 of 200 = 1.5% | 0.5% to 4.3% | 1 | 14 of 57 = 24.6% | 7.0% | 1.6% | 5.3% | yes, below 5% |
| MedMCQA 4, + GPT-4o (medmcqa4_gpt4o) | 11 of 200 = 5.5% | 3.1% to 9.6% | 1 | 71 of 301 = 23.6% | 6.6% | 4.3% | 7.6% | yes, includes 5% |
| HELM panel A (helm_A) | 8 of 200 = 4.0% | 2.0% to 7.7% | 1 | 20 of 104 = 19.2% | 6.7% | 2.2% | 6.7% | yes, includes 5% |
| HELM panel B (helm_B) | 5 of 200 = 2.5% | 1.1% to 5.7% | 1 | 20 of 41 = 48.8% | 7.3% | 1.4% | 7.3% | yes, includes 5% |
| all seven pooled (descriptive, not in the plan) | 47 of 1,400 = 3.4% | 2.5% to 4.4% | 7 of 7 | | | | | descriptive only |

Decision statement from the plan: the flag behaves as specified in a configuration if the lower bound of its interval is at or below 5%. That holds in all seven configurations, so the flag behaves as specified overall (the rule cannot distinguish 5% from about 8% at R = 200). No configuration fires more often than expected: the highest rate is 5.5% (MedMCQA 4), and its interval, 3.1% to 9.6%, includes 5%. The pooled row was not in the plan and is descriptive only; it treats the seven configurations as sharing one rate, which they need not.

Contrast with the real data. In every configuration the real unanimous-wrong rate is above the largest unanimous-wrong rate seen in any of the 200 null replicates of that configuration (real 41.9% against a null maximum of 16.1%, 33.6% against 9.8%, 26.0% against 12.3%, 24.6% against 5.3%, 23.6% against 7.6%, 19.2% against 6.7%, 48.8% against 7.3%). The real flag is therefore not within the range the null produces, by a wide margin, in all seven configurations. The null replicates have the same models, accuracies, error sets and letter habits as the real data.

## Interpretation

Calibration. Under this null every configuration's flag rate is consistent with 5% or below (every interval includes 5% or lies below it); the highest is 5.5% (MedMCQA 4). Two configurations, MedQA 3 mid-tier and MedQA 5, are conservative (1.5% each, upper bounds 4.3%). The flag's strict rule (rate above the 95th percentile) leaves ties unflagged: the null rate equalled the permutation 95th percentile exactly in 5, 6, 13, 27, 6, 5 and 18 of the 200 replicates in the seven configurations (in the order of the table), which contributes to the low rates, most of all in MedQA 5 (57 all-wrong questions) and HELM panel B (41).

Where the flag fired. Of the 47 null flags, the largest counts are MedMCQA 4 (11), MedQA 4 with GPT-4o (9), and 8 each for MedQA 4 with DeepSeek-V3 and HELM panel A. With seven configurations, one interval could exclude 5% from above by chance even for a calibrated flag; none did. The study is not powered to detect a true flag rate of 7 or 8%: with 200 replicates and about 10 flags, the Wilson interval runs from about 2.3 points below to 4.0 points above the estimate, and the plan's rule would declare a configuration anti-conservative only at 17 or more flags (exact binomial chance of that about 0.24 if the true rate were 7%, 0.43 at 8% and 0.79 at 10%).

Near-constant Llama 3.1 8B in HELM panel A. This configuration includes a model that answered B on 955 of 1,000 questions. Because the null keeps each model's letter habits, the replicates keep that near-constant B. The flag rate is 4.0% (8 of 200, interval 2.0% to 7.7%), so the flag stayed quiet when shared question-level errors were absent even though a member is near-constant. This is a different statement from the v0.1.1 pair results, where the flag stayed quiet for Llama pairs on real data: here the real data of panel A raises the flag, and it does so because the other four models share wrong B answers beyond their letter habits (as set out in RESULTS_v0.1.1.md), which is exactly what the null removes. In 5 of the 200 panel A replicates the null rate equalled the permutation 95th percentile exactly, so ties are not a large source of the low rate there. This result concerns the five-model panel and not the Llama pairs, which were not run in the null.

Permutation baseline against the null. The real-data permutation 95th percentile is at or above the empirical 95th percentile of the 200 null unanimous-wrong rates in every configuration: 15.1% against 14.3%, 7.0% against 7.0%, 11.0% against 8.2%, 7.0% against 5.3%, 6.6% against 6.3%, 6.7% against 4.8% and 7.3% against 4.9% (table order, real against null). The permutation baseline is thus slightly conservative relative to this null, by up to 2.7 points (MedQA 4 with GPT-4o), which fits the pooled flag rate of 3.4% being below 5%. The mean of the replicates' own permutation 95th percentiles is 14.6%, 6.7%, 8.0%, 4.1%, 6.1%, 4.6% and 4.7%.

## Correction after the results

A reviewer of this release pointed out, after the results were in, that this null is a special case of the flag's own permutation hypothesis. In each replicate a model's wrong answer depends only on the reference letter and the number of options, which is exactly the stratum within which the permutation baseline shuffles answers, and models are drawn independently. Under that condition the within-stratum permutation test is exact by construction, so a flag rate at or below about 5% was expected from theory before any replicate was run. The plan was wrong on this point where it calls the redraw an independent mechanism and says the rate is not guaranteed to be at or below 5%. The plan is left as committed.

So this control checks that the flag is implemented correctly and that its Monte Carlo calibration holds on the real error sets and accuracies. It is not a test of specificity against the ways the flag could fire falsely on real data, such as independent but question-dependent habits (position or length preferences, distractors that attract several models for different reasons), which the permutation cannot absorb and this null cannot produce. The specificity question raised in outside/RESULTS_v0.1.1.md remains open; a control with independently randomised option order, which needs new model runs, is still owed.

## What this does and does not show

It shows that the unchanged v0.1.0 flag rules, on the real error sets, accuracies and letter habits of seven real configurations, give flag rates consistent with 5% or below when shared wrong-letter choices are removed by construction (the questions every model gets wrong are kept), as theory predicts for this null, and that the real data lie far outside it. It does not answer the specificity question raised in outside/RESULTS_v0.1.1.md, which remains open.

It does not show more than that.

- It is semi-synthetic. The wrong answers are generated by the study design, not produced by models. Real models' wrong answers depend on the question text, which this null cannot reproduce.
- It tests calibration under one specific null: independent draws from each model's marginal wrong-letter distribution. Shared errors can be absent in other ways, for example models whose errors follow different but question-dependent patterns, or letter habits that depend on the reference letter. The null uses each model's marginal distribution restricted to distractors, not one conditional on the reference letter, so reference-letter-specific habits are not kept.
- It holds the all-wrong set fixed. How the flag behaves when models' errors are independent across questions in the sense of different error sets, with different all-wrong counts and different denominators, is not tested.
- It says nothing about sensitivity at small margins. The real flags clear the null by wide margins; this study does not show that smaller true shared-error effects would be detected.
- The flag rate is estimated from 200 replicates per configuration. An interval of 2% to 8% is consistent with 5%, with a true rate of 7% or 8% as well; it is not evidence of exactly 5%.
- Pairs, the shared-letter-preference limit in PROTOCOL.md section 8, and the layers module are not covered. Nothing here concerns patients, free-text answers or adoption.
