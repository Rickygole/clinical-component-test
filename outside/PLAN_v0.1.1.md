# Outside-data run for v0.1.1: plan

Written and committed on 2026-11-12, before any prediction file from the source below was downloaded. Only the HELM Lite run index (runs_to_run_suites.json) and one directory listing were read beforehand.

## Purpose

Run the agreement test of cctest v0.1.0, unchanged, on per-question answers that another group published, to see how it behaves on data its author did not produce.

## Source

Stanford CRFM, HELM Lite, release v1.13.0, scenario MedQA (`med_qa`), public bucket `crfm-helm-public`, path `lite/benchmark_output/runs/<suite>/med_qa:model=<model>/`. Files used per model: `instances.json` (question ids and the reference option) and `display_predictions.json` (the model's output). `per_instance_stats.json` is used only to cross-check correctness. No question text is shipped.

## Panels, fixed now

Each panel has one model per developer, using the five developers in the ICDM 2026 study (Meta, Alibaba, Google, DeepSeek, OpenAI). DeepSeek has no small model in HELM Lite, so Mistral AI takes that place in panel A.

Panel A, small and mid-size models:
- meta_llama-3.1-8b-instruct-turbo (suite v1.7.0)
- qwen_qwen2.5-7b-instruct-turbo (v1.9.0)
- google_gemma-2-9b-it (v1.6.0)
- openai_gpt-4o-mini-2024-07-18 (v1.6.0)
- mistralai_mistral-7b-instruct-v0.3 (v1.4.0)

Panel B, large models:
- meta_llama-3.1-405b-instruct-turbo (v1.7.0)
- qwen_qwen2.5-72b-instruct-turbo (v1.9.0)
- google_gemini-1.5-pro-002 (v1.10.0)
- deepseek-ai_deepseek-v3 (v1.13.0)
- openai_gpt-4o-2024-08-06 (v1.10.0)

## Extraction rule, fixed now

- case_id: the HELM instance id. Only instances present for every model in a panel are used; any other instance is reported, not silently dropped.
- reference_answer: the letter of the reference tagged `correct`, letters assigned A, B, C, ... in the order the references are listed.
- answer: the first character of the stripped `predicted_text` if it is one of those letters, otherwise empty (counted as unscored by cctest).
- n_options: the number of references for the instance.
- Check: for every model, correctness from this rule must agree with HELM's per-instance `exact_match`; disagreements are reported.

## Analyses, fixed now

- Primary: `cctest agreement` on panel A and on panel B, with the v0.1.0 code (tag v0.1.0), 10,000 permutations, seed 42, and the unchanged limits file examples/limits_example.json.
- Secondary: every two-model pair within each panel (20 pairs).
- The flag rule, baselines, intervals and limits are those of v0.1.0. Nothing is changed after the data are seen. Every result is reported, whether or not the flag fires.

## What will be recorded

Download date and time, the SHA-256 of every downloaded file, the extraction script, the extracted CSV, all report JSONs, and a short results section in CHANGELOG.md under v0.1.1.
