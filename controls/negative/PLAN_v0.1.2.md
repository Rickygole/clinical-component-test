# Negative control for v0.1.2: plan

Written before any replicate dataset was generated and before the cctest agreement test was run on any semi-synthetic data. The generator, make_null.py, is committed together with this plan. Its only runs before the commit were on a 300-question toy file of uniformly random answers (not on any ICDM or HELM file), to check that the script executes; the results of that toy run are discarded and not used.

## Purpose

Every real configuration tested in v0.1.0 and v0.1.1 raised the convergent_failure flag. That shows sensitivity to shared errors in real data. It does not show that the flag stays quiet when shared errors are truly absent. This control builds datasets in which question-level shared wrong answers are absent by construction, keeps everything else real, and measures how often the unchanged v0.1.0 flag fires.

## Design

Semi-synthetic null. For each real configuration, and for each of the R replicate datasets:

- Every model's real per-question correctness is kept exactly. A correct answer stays correct and the same letter; an invalid or missing answer is left as it is. So accuracy, the set of questions each model gets wrong, the all-wrong set, the number of options and the reference letters are real and identical in every replicate.
- Each wrong answer is replaced by an independent random draw. The draw is from that model's own wrong-letter distribution (counts of the letters it gave on its real, valid, wrong answers across the whole file), restricted to the distractors of that question and renormalised. If the model has no mass on any distractor of that question, the draw is uniform over the distractors. This mirrors the renormalisation in the model-expectation baseline of PROTOCOL.md section 4.
- Draws for different models and different questions are independent, so no question-level shared preference exists by construction. Each model keeps its letter habits (for example, the near-constant answer B of Llama 3.1 8B in HELM panel A).
- The generator asserts, for every replicate, that correctness, validity, ordering and option range are preserved.

Why this design and not another. Permuting answers across questions would be the same mechanism the baseline uses and would test it against itself; redrawing from the model's own marginal wrong-letter distribution is an independent mechanism (sampling with replacement from a marginal, rather than a within-stratum permutation of the observed values). Keeping the real error sets keeps the denominators and sparsity that real configurations have, which is where specificity is hardest.

Known property of this design. The permutation baseline is conditional on the observed answers of each replicate and permutes within strata of reference letter and option count, whereas the null redraws fresh. These are two different null mechanisms for the same independence hypothesis, so the flag rate is not guaranteed to equal 5% exactly; a modest departure in either direction is expected from the discreteness and from the loss of reference-letter-specific habits (the null uses each model's marginal wrong-letter distribution, not one conditional on the reference letter). The flag rule is strict (rate above the 95th percentile), so ties do not flag.

## Configurations, fixed now

Five ICDM Table I configurations (data/icdm2026/), with mid-tier = llama3_8b, qwen25_7b, gemma3n_e4b:

1. medqa3_mid: MedQA, mid-tier (3 models)
2. medqa4_deepseek: MedQA, mid-tier + deepseek_v3
3. medqa4_gpt4o: MedQA, mid-tier + gpt4o
4. medqa5_all: MedQA, mid-tier + deepseek_v3 + gpt4o
5. medmcqa4_gpt4o: MedMCQA, mid-tier + gpt4o

HELM panels, as in outside/COMMANDS.md (outside/data/helm_lite_medqa_answers.csv):

6. helm_A: the five panel A models
7. helm_B: the five panel B models

The exact model lists are in make_null.py.

## Replicates and seeds, fixed now

R = 200 replicates per configuration, 1,400 in all. Configuration i (1 to 7 in the order above) and replicate r (1 to 200) use generator seed 100000 * i + r. The cctest seed (42) and permutations (10,000) are the v0.1.0 defaults, unchanged. Replicate 0 in the run is the real data, with no generator seed. R is not lowered: one v0.1.0 run takes a few seconds and the runs are spread over several processes.

## Code

The unchanged v0.1.0 command line, installed from the v0.1.0 tag in a separate virtual environment: `cctest agreement <csv> --models <list> --out <report>` with default permutations and seed. No limits file is passed, since the flag does not depend on limits. Nothing in src, tests, examples, README, CHANGELOG or PROTOCOL is changed.

## Outcome measured

Primary: per configuration, the flag rate = number of the 200 replicates in which convergent_failure is raised, over 200, with a Wilson 95% interval. The real-data flag (1 for every configuration in v0.1.0 and v0.1.1) is reported beside it.

Per replicate record: configuration, replicate, seed, unanimous-wrong count and all-wrong count, unanimous-wrong rate, permutation 95th percentile, flag.

Also reported, descriptive only: the largest and the mean unanimous-wrong rate over the 200 replicates against the real unanimous-wrong rate and the real permutation 95th percentile, so that the contrast is shown in rates and not only in flags.

## Decision statement, fixed now

The flag behaves as specified in a configuration if the Wilson 95% interval of its flag rate includes 5% or lies entirely below 5%, that is, if the lower bound is at or below 0.05. The flag behaves as specified overall if this holds in all seven configurations.

If the lower bound of the interval is above 0.05 for a configuration, the report says that the flag fires more often than its nominal 5% under this null in that configuration, gives the rate, and treats it as a limitation of v0.1.0 (anti-conservative in that configuration). Nothing about the flag rule, the baseline, the generator or R is changed after the results are seen, and no configuration, replicate or seed is dropped. If the flag rate is far below 5% in a configuration, it is reported as conservative: specificity is shown there but sensitivity at that margin is not.

Two readings are fixed in advance. First, with seven configurations, one interval can exclude 5% by chance even when the flag is calibrated; the report counts and names such cases and does not explain them away. Second, passing this control shows calibration under one null only: no shared question-level preference conditional on the real error sets. It does not show the flag stays quiet for every way shared errors can be absent.

## What will be recorded

This plan and its commit hash and time; make_null.py; replicates_v0.1.2.tsv (all 1,400 replicates); real_data_v0.1.2.tsv; one example report JSON per configuration for replicate 1 and for the real data (examples/); RESULTS_v0.1.2.md; COMMANDS.md. Everything is reported, whether or not the flag fires.
