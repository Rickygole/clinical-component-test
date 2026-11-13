# Commands for the v0.1.1 outside-data run

Run from the repository root. `cctest` is the v0.1.0 release, installed with `pip install git+https://github.com/Rickygole/clinical-component-test@v0.1.0`.

Download (one line per file in SOURCES.tsv; each `url` column there is the exact source):

    curl -s -o <model>/<file> https://storage.googleapis.com/crfm-helm-public/lite/benchmark_output/runs/<suite>/med_qa:model=<model>/<file>

Extraction:

    python3 -I outside/extract_helm.py <download folder> outside/data/helm_lite_medqa_answers.csv

Panel A:

    cctest agreement outside/data/helm_lite_medqa_answers.csv --models meta_llama-3.1-8b-instruct-turbo,qwen_qwen2.5-7b-instruct-turbo,google_gemma-2-9b-it,openai_gpt-4o-mini-2024-07-18,mistralai_mistral-7b-instruct-v0.3 --limits examples/limits_example.json --out outside/reports/panel_A.json

Panel B:

    cctest agreement outside/data/helm_lite_medqa_answers.csv --models meta_llama-3.1-405b-instruct-turbo,qwen_qwen2.5-72b-instruct-turbo,google_gemini-1.5-pro-002,deepseek-ai_deepseek-v3,openai_gpt-4o-2024-08-06 --limits examples/limits_example.json --out outside/reports/panel_B.json

Pairs, for each two models a and b within a panel P:

    cctest agreement outside/data/helm_lite_medqa_answers.csv --models a,b --limits examples/limits_example.json --out outside/reports/pairs/P__a__b.json

Post hoc, not in the plan:

    cctest agreement outside/data/helm_lite_medqa_answers.csv --models qwen_qwen2.5-7b-instruct-turbo,google_gemma-2-9b-it,openai_gpt-4o-mini-2024-07-18,mistralai_mistral-7b-instruct-v0.3 --limits examples/limits_example.json --out outside/reports/post_hoc/panel_A_without_llama_3.1_8b.json

All runs use the defaults of v0.1.0: 10,000 permutations, seed 42.
