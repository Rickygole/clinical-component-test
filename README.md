# cctest

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24183594.svg)](https://doi.org/10.5281/zenodo.24183594)

Every version is archived on Zenodo. The concept DOI 10.5281/zenodo.24183594 resolves to the latest version. Version 0.1.0: https://doi.org/10.5281/zenodo.24183595. Version 0.1.1: https://doi.org/10.5281/zenodo.24183862.

cctest: pre-release checks for clinical AI systems that combine components. This is v0.1.2: the code of the first public version (v0.1.0) plus an outside-data run (v0.1.1), a negative control and a layer test on public benchmarks (v0.1.2). It packages two checks and reproduces the published analyses they come from. It is designed to let teams check, before deployment, two things about a system built from several parts.

1. Agreement test for combined language models. When several models answer the same multiple-choice question and all agree, how often is the shared answer wrong, and do the models share wrong answers more often than a permutation baseline predicts?
2. Data-layer test for multi-input fusion models. What does adding each data layer do to held-out AUROC, and does any layer fail to exceed chance on its own?

Both modules write the same JSON report. The protocol that fixes the intervals, baselines, flags and decision rule is in [PROTOCOL.md](PROTOCOL.md) (PDF copy: PROTOCOL.pdf).

This release makes no claim of adoption, validation on patients, or regulatory status. The worked examples use exam questions and one public cohort. See Limits.

## Install

Python 3.9 or newer. Dependencies are numpy and scipy.

    pip install .

For the tests, use `pip install ".[test]"`. `make test` and `make reproduce` run from the repository root without installing.

## Module 1: agreement

    cctest agreement data/icdm2026/medqa_answers.csv --models llama3_8b,qwen25_7b,gemma3n_e4b,deepseek_v3,gpt4o --limits examples/limits_example.json --out report.json

Flags: `--models` (required, comma separated model_id values), `--permutations` (default 10000), `--seed` (default 42), `--limits` (JSON file of acceptable limits), `--out` (write the report to a file instead of stdout).

Input CSV, one row per (case_id, model_id), with exactly these required columns:

| column | meaning |
| --- | --- |
| case_id | identifier of the question or case |
| model_id | identifier of the model |
| answer | the model's answer letter (A, B, C and so on) |
| reference_answer | the correct letter |
| n_options | number of answer options for that case |

The shipped files also carry a developer column. It is not read by the code. The code rejects the input, with a message on stderr and exit code 2, for an empty file, missing columns, duplicated (case_id, model_id) pairs, models that disagree on reference_answer or n_options for a case, and unequal coverage across the chosen models. A case with a missing or invalid answer for any chosen model is not dropped silently: it is excluded from scoring and the count is written in the report notes.

## Module 2: layers

    cctest layers data/sgof2026/fold_auroc.csv --oof data/sgof2026/oof_predictions.csv --limits examples/limits_example.json --out report.json

Flags: `--oof` (out-of-fold predictions, enables patient-level intervals), `--seed` (default 2026), `--limits`, `--out`.

Fold file (required), one row per model, layer, condition, repeat and fold:

    model_id,layer,condition,repeat,fold,auroc

`condition` is `with` (model trained with the layer), `without` (same model trained without it) or `solo` (a model using that layer alone). Every model must share the same repeat by fold grid, and each `with` row set needs a matching `without` set. Folds must be identical across conditions.

Out-of-fold file (optional):

    model_id,layer,condition,repeat,patient_id,probability,label

`label` is the binary outcome. Patients and labels must be identical across the models in the file.

Limits file, for both modules:

    {"recorded": "2026-11-12", "limits": {"unanimous_wrong_rate": 0.10}}

Keys under `limits` are the test names listed below, each a number or an object with a `value`. `examples/limits_example.json` holds illustrative limits for the worked examples only. They are not recommendations. Each team should record its own limits before running the test.

## Report fields

Top level: `tool`, `tool_version`, `module`, `run_date`, `inputs` (SHA-256 of each input file), `entries`, `flags`, `notes`, `scope`.

Each entry: `test`, `unit`, `components` (model or layer identifiers), `count`, `denominator`, `estimate`, `lower_95`, `upper_95`, `acceptable_limit`, `limit_recorded` (date), `decision`. An inconclusive decision on a proportion also carries `denominator_needed`. Entries can carry extra fields, for example `baselines` or `patient_lower_95`.

Tests: agreement writes `agreed_answer_error_rate`, `unanimous_wrong_rate` and `agreed_wrong_exposure`, all with Wilson 95% intervals. Layers writes `solo_layer_auroc` and `auroc_loss_from_adding_layer` (AUROC without the layer minus AUROC with it, so a positive value means the layer hurt), with the signed change also reported.

Decision values: `supports reliance`, `fails`, `inconclusive`, `no limit recorded`. Example reports are in `examples/reports/`.

## Tests and reproduction

    make test
    make reproduce

`make test` runs 36 tests, which pass. They include Wilson intervals checked against a reference implementation, the zero-event and all-wrong cases, and rejection of malformed input (labels that are not 0 or 1, labels that change across repeats, misaligned repeats, impossible option counts).

`make reproduce` recomputes 81 values from the two source papers (80 printed values and one rerun target, the 520 agreed cases) using the shipped files and compares each at the printed precision. Current result: ICDM 2026, 35 of 35 checks pass. SGOF, 44 pass and 2 documented differences, 0 fail. The two differences are the bounds of the patient-level interval for the SGOF change (CHANGELOG, difference 4). The differences and other findings are listed in [CHANGELOG.md](CHANGELOG.md) and are not tuned away.

## Outside-data run (v0.1.1)

The agreement test was run, unchanged, on MedQA outputs that Stanford CRFM published for ten models in HELM Lite. The panels and the extraction rule were committed before the outside files were downloaded. Both five-model panels raise the convergent_failure flag. See [outside/RESULTS_v0.1.1.md](outside/RESULTS_v0.1.1.md).

## Negative control and public multi-omic benchmarks (v0.1.2)

Negative control: for seven real configurations, every model's correctness was kept and its wrong answers were redrawn independently, so shared errors are absent by construction. The plan was committed before any replicate was generated. The flag fired in 47 of 1,400 replicates (3.4%, 2.5% to 4.4%), and in all seven real datasets. See [controls/negative/RESULTS_v0.1.2.md](controls/negative/RESULTS_v0.1.2.md).

Layer test on public benchmarks: the unchanged layer test was run on the ROSMAP and BRCA benchmarks with an added noise layer, results already reported in the SGOF paper. It flags the noise layer in both and reproduces the published losses. See [outside_layers/RESULTS_v0.1.2.md](outside_layers/RESULTS_v0.1.2.md).

## Data and sources

The ICDM data are answer letters from five language models and one control model on MedQA and MedMCQA, with case index numbers only and no question text. The SGOF data are derived predictions and fold AUROCs from a public depression cohort, with no genotype, expression or methylation values. Terms are in [NOTICE](NOTICE).

Source papers, checked against their camera-ready versions:

- Ricky Gole and Jamell Dacon. "Detecting and Mitigating Convergent Failures in Clinical LLM Ensembles." IEEE International Conference on Data Mining (ICDM), 2026.
- Ricky Gole, Oluwasegun Soji-John, Gabriel Chambers, Sharon Iweha, Peyton Blake and Jamell Dacon. "Diagnosing and Mitigating Modality Dominance in Multi-Omic Antidepressant Response Prediction." IEEE BIBM 2026 workshop. The method it proposes is called SGOF (signal-gated omic fusion).

## License

Code: MIT, see [LICENSE](LICENSE). Shipped data files under `data/` are CC BY 4.0 for the author's contributions, with the carve-outs listed in NOTICE. The HELM-derived file under `outside/data/` is not relicensed (see NOTICE). Underlying dataset and model terms are in NOTICE.

## Limits

- Exam questions are not patients. Nothing here has been validated on patient data.
- One multi-omic cohort of 111 patients, and two exam datasets. Results from them do not carry to other settings.
- The ICDM model outputs were collected in April to May 2026, and the HELM Lite outputs at the dates of their HELM releases. Hosted models change over time.
- The permutation baseline does not flag a shared letter preference: if every model always picks the same wrong letter for a given correct letter, the test attributes it to individual tendencies. A test documents this.
- Folds within a repeat share training patients, so layer intervals are optimistic about new patients. Both AUROC intervals resample fixed predictions and ignore retraining. The interval over repeat means reflects split-to-split variation only and narrows as repeats are added without new patients, so it is not a sampling interval. Decisions use the patient interval whenever out-of-fold predictions are supplied. Without them, a layer decision of "supports reliance" rests on the interval over repeat means and is provisional.
- The flag rule was fixed on 2026-11-12, the same day the worked examples were re-analysed. The examples are not a prospective test of the rule.
- Discrete outputs only (answer letters, binary labels). Free text is not handled in v0.1.
- Results are evidence for a developer's decision, not a safety certification or a clinical safety finding.
