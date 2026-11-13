# Outside-data run for v0.1.1: results

## Timeline

The plan in PLAN_v0.1.1.md was committed at 2026-11-13 03:24:05 UTC (commit e864159). GitHub's activity log for the repository records the push at 03:24:06 UTC (GitHub REST API, `GET /repos/Rickygole/clinical-component-test/activity`, push event with `after` = e864159f9e3d467d594461ddaaefe542911eb58c). The 30 source files were downloaded from 03:24:17 to 03:24:32 UTC, after that push. Every file's download time, URL and SHA-256 are in SOURCES.tsv.

## Source

Stanford CRFM, HELM Lite, release v1.13.0, MedQA scenario: 1,000 questions per model, five-shot prompts written and run by HELM, not by the author of cctest. Reference: P. Liang et al., "Holistic Evaluation of Language Models," Transactions on Machine Learning Research, 2023 (arXiv:2211.09110). The per-instance outputs are public in the `crfm-helm-public` bucket. No license for those outputs was found stated at the source when read on 2026-11-12 (see NOTICE).

## What was run

- Extraction: outside/extract_helm.py, following the plan. For all ten models, correctness from the extracted letters agrees with HELM's per-instance exact_match on every question (0 disagreements, 0 missing; console output in extract_log.txt). The extracted file is data/helm_lite_medqa_answers.csv (SHA-256 dc4963b0f7ba742c07a13572f2a527ecc44ef848ef4187f10e61087a41e0e812). After the run, the script was changed only to count and report missing statistics and to drop an unused fallback; rerunning it gives a file with the same SHA-256.
- Code: cctest installed from the v0.1.0 tag (commit 48badb3). `git diff v0.1.0 -- src tests examples/limits_example.json pyproject.toml` is empty for this release. Limits: examples/limits_example.json, unchanged. The exact commands are in COMMANDS.md.
- HELM accuracies on these 1,000 questions: Llama 3.1 8B 26.6%, Qwen 2.5 7B 57.7%, Gemma 2 9B 60.5%, GPT-4o mini 74.4%, Mistral 7B v0.3 49.6%, Llama 3.1 405B 85.3%, Qwen 2.5 72B 75.6%, Gemini 1.5 Pro 77.0%, DeepSeek-V3 81.1%, GPT-4o 86.9%.

## Primary results

| panel | unanimous-wrong rate | permutation 95th percentile | ratio to permutation mean | flag | error rate among agreed answers |
| --- | --- | --- | --- | --- | --- |
| A, small and mid-size | 20 of 104 = 19.2% (12.8% to 27.8%) | 6.7% | 4.8 | raised | 20 of 111 = 18.0% (12.0% to 26.2%) |
| B, large | 20 of 41 = 48.8% (34.3% to 63.5%) | 7.3% | 18.5 | raised | 20 of 630 = 3.2% (2.1% to 4.9%) |

Reports: reports/panel_A.json and reports/panel_B.json.

Panel B. Among the 41 questions all five large models missed, all five chose the same wrong answer on 20, and those 20 shared answers are spread evenly over the four letters (5 each). When the five large models agreed, their shared answer was wrong on 3.2% of those questions. Against the illustrative 5% limit that rate supports reliance, while the unanimous-wrong rate fails the illustrative 10% limit. The two numbers answer different questions: how often agreement is wrong, and whether the errors that remain are shared.

Panel A. In HELM's run, Llama 3.1 8B answered B on 955 of 1,000 questions, so its 26.6% accuracy is close to the share of B among the reference answers (231 of 1,000). It is a near-constant responder, not a random one. Agreement among the five smaller models was rare (111 of 997 scored questions) mostly because every agreed answer had to be B or one of Llama's few other letters, and 19 of the 20 unanimous-wrong answers are B. A member that always gives the same letter is held fixed by the stratified permutation, so panel A's flag mainly tests whether the other four models chose a wrong B together more often than their own letter habits predict. This is the shared-letter-preference limit in PROTOCOL.md, section 8. This explanation was written after the results were seen; the analyses were not changed.

## Secondary results

Under the pre-specified seed, 18 of the 20 two-model pairs raise the flag (reports/pairs/).

- All ten pairs in panel B raise it, with unanimous-wrong rates of 65.2% to 77.3% against 95th percentiles of 41.4% to 47.1%.
- Every pair of the four panel A models other than Llama 3.1 8B raises it, by 19 to 29 points above the 95th percentile.
- The four pairs that include Llama 3.1 8B are uninformative for the reason above. Two raise the flag by 0.3 points (Llama with Qwen 2.5 7B, 161 of 345 against a 95th percentile of 160 of 345; Llama with Mistral, 147 of 372 against 146 of 372). One equals its 95th percentile exactly and is not flagged only because the rule requires a rate above it (Llama with GPT-4o mini, 69 of 186). One falls 0.7 points below (Llama with Gemma 2 9B). An independent check with 20 other seeds found the Llama with Qwen pair flagged in 19 of 20, so the pair count of 18 depends on the seed by one pair. The two panel flags do not.
- The Llama with Qwen pair is also the only one of the 20 flagged configurations (18 pairs and 2 panels) whose rate is below the closed-form model expectation (ratio 0.97). The v0.1.0 flag compares only with the permutation baseline. A v0.2 could require a rate above both baselines and could screen out near-constant members before testing. Neither change is made here, because the rule was fixed before the data were seen.

## Post hoc analysis (not in the plan)

Panel A without Llama 3.1 8B, the four remaining models (reports/post_hoc/panel_A_without_llama_3.1_8b.json): 58 of 135 questions missed by all four received the same wrong answer from all four, 43.0% (34.9% to 51.4%), against a permutation 95th percentile of 9.6% (ratio to the permutation mean 7.0). These 58 shared answers are spread over the letters (A 19, B 19, C 11, D 9). The flag is raised. This analysis was added after the results were seen and is reported separately from the pre-specified ones.

## What this does and does not show

It shows that the agreement test runs unchanged on per-question outputs published by another group, and that shared wrong answers of the kind reported in the ICDM paper also appear in models, prompts and a question sample chosen by someone else. It uses the same benchmark, MedQA, so it does not test a new task. It does not show anything about patients, about free-text answers, or about whether any team has adopted the test. The illustrative limits are the author's and are not recommendations.
