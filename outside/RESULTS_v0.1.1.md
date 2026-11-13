# Outside-data run for v0.1.1: results

The plan in PLAN_v0.1.1.md was committed and pushed at 2026-11-12 22:24:05 (UTC-5), commit e864159. The 30 source files were downloaded from 2026-11-13 03:24:17 UTC onward, after that commit. Every file's download time, URL and SHA-256 are in SOURCES.tsv.

## What was run

- Source: Stanford CRFM, HELM Lite v1.13.0, MedQA, 1,000 questions per model, five-shot prompts written and run by HELM, not by the author of cctest.
- Extraction: outside/extract_helm.py, following the plan. For all ten models, correctness from the extracted letters agrees with HELM's per-instance exact_match on every question (0 disagreements). The extracted file is data/helm_lite_medqa_answers.csv (SHA-256 dc4963b0f7ba742c07a13572f2a527ecc44ef848ef4187f10e61087a41e0e812).
- Code: cctest installed from the v0.1.0 tag (commit 48badb3). The package source in this release is byte-identical to v0.1.0. Limits: examples/limits_example.json, unchanged.
- HELM accuracies on these 1,000 questions: Llama 3.1 8B 26.6%, Qwen 2.5 7B 57.7%, Gemma 2 9B 60.5%, GPT-4o mini 74.4%, Mistral 7B v0.3 49.6%, Llama 3.1 405B 85.3%, Qwen 2.5 72B 75.6%, Gemini 1.5 Pro 77.0%, DeepSeek-V3 81.1%, GPT-4o 86.9%.

## Primary results

| panel | unanimous-wrong rate | permutation 95th percentile | ratio to permutation mean | flag | error rate among agreed answers |
| --- | --- | --- | --- | --- | --- |
| A, small and mid-size | 20 of 104 = 19.2% (12.8% to 27.8%) | 6.7% | 4.8 | raised | 20 of 111 = 18.0% (12.0% to 26.2%) |
| B, large | 20 of 41 = 48.8% (34.3% to 63.5%) | 7.3% | 18.5 | raised | 20 of 630 = 3.2% (2.1% to 4.9%) |

Reports: reports/panel_A.json and reports/panel_B.json. In panel B, among the 41 questions all five large models missed, all five chose the same wrong answer on 20. When the five large models agreed, their shared answer was wrong on 3.2% of those questions. Against the illustrative 5% limit, that rate supports reliance, while the unanimous-wrong rate fails the illustrative 10% limit. The two numbers answer different questions: how often agreement is wrong, and whether the errors that remain are shared. In panel A, agreement among the five smaller models was rare (111 of 997 scored questions) and wrong on 18.0% of them, which fails the 5% limit.

## Secondary results

18 of the 20 two-model pairs raise the flag (reports/pairs/). All ten pairs in panel B raise it, with unanimous-wrong rates of 65.2% to 77.3% against 95th percentiles of 41.4% to 47.1%. In panel A the two pairs that do not raise it both include Llama 3.1 8B, whose HELM accuracy here (26.6%) is close to chance. Its two pairs that do raise it pass the threshold by 0.3 points, while every pair of the other four models passes it by 19 to 29 points. This matches the specificity limit stated in PROTOCOL.md: a near-random member contributes little shared structure, and a flag is driven by the members that converge.

## What this does and does not show

It shows that the agreement test runs unchanged on per-question outputs published by another group, and that the convergence reported in the ICDM paper also appears in models, prompts and a question sample chosen by someone else. It does not show anything about patients, about free-text answers, or about whether any team has adopted the test. The illustrative limits are the author's and are not recommendations.
