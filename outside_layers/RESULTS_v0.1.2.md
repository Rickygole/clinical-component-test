# Data-layer test on two public benchmarks, from existing results

Run date 2026-11-12. Unchanged cctest v0.1.0 `layers` command, seed 2026, illustrative limit 0.02 from `examples/limits_example.json` (not a recommendation).

## Source and provenance

- Results file: the public-benchmark experiment of the SGOF paper (Gole et al., IEEE BIBM 2026 workshop, section IV-H), notebook `ceamls_17_public_benchmarks`, outputs `results/public/public_rosmap.json` and `public_brca.json` in the SGOF camera-ready repository.
- Who ran the models: the package author, in the SGOF study. Nothing was rerun for this exercise. The JSON files were only read and reshaped into the package fold format.
- Datasets: the ROSMAP and BRCA multi-omic benchmarks as bundled in the MOGONET repository (github.com/txWang/MOGONET, commit 32d9066b7fe289b3f7cdb496a5668834079c274c, train and test rows concatenated). Citation: T. Wang et al., Nature Communications 12(1):3445, 2021. License of the bundled files: none declared. The MOGONET repository has no license file (checked on 2026-11-12 through the GitHub API, which reports no license for txWang/MOGONET). No patient-level values are redistributed here, only per-fold AUROCs.
- ROSMAP: Alzheimer disease vs normal control, 351 patients (182 positive). BRCA: binary contrast of two PAM50 subtypes, 583 patients (147 positive). Real layers: mRNA, DNAm, miRNA. Every layer, the noise layer included, is reduced inside each training fold to the 200 features most associated with the label (SelectKBest with the ANOVA F statistic, notebook ceamls_17, function prep_layer), so the models see the 200 noise features that happen to fit the training labels best.
- The noise layer is synthetic: 100,000 iid standard normal features, a fresh draw per repeat (seed equal to the repeat index), appended as an extra layer.
- Design: 5 repeats of 5 stratified folds. The "with" and "without" conditions share folds, seeds and inner splits.
- Methods: naive concatenation of GCN encoders; SGOF; a late-fusion MLP; and "mogonet_style", an in-house re-implementation and not the official MOGONET code. Solo rows are a one-layer GCN (the naive model on a single layer).

## What was in the JSON

Per-fold AUROC for every method in both conditions (repeats[rep][real or noise][method].auroc, 5 values per repeat), so a full 5 by 5 grid exists and nothing was fabricated. Solo AUROCs exist for the three real layers (in the "real" condition) and for the noise layer alone (in the "noise" condition). Not present: out-of-fold probabilities or labels, so no patient-level intervals are possible. Fold ids are positional (0 to 4); the JSON does not record which patients are in each fold.

Mapping: condition "with" = noise layer added, "without" = real layers only, layer name "noise". The package loss is AUROC without minus with, so it equals minus the paper's "noise minus real" difference.

## Results

Loss = AUROC without the noise layer minus with it; positive means the noise layer hurt. Intervals are the paired bootstrap over the 5 repeat means. Decision under the illustrative 0.02 limit.

ROSMAP (351 patients)

| Method | AUROC with noise | AUROC without | Loss | 95% interval | Decision |
| --- | --- | --- | --- | --- | --- |
| naive concatenation | 0.559 | 0.765 | 0.206 | 0.159 to 0.253 | fails |
| mogonet_style (re-implementation) | 0.610 | 0.793 | 0.183 | 0.147 to 0.220 | fails |
| late-fusion MLP | 0.846 | 0.871 | 0.026 | 0.021 to 0.029 | fails |
| SGOF | 0.780 | 0.786 | 0.006 | -0.002 to 0.015 | supports reliance (provisional) |

Solo AUROC: mRNA 0.739 (0.729 to 0.751), DNAm 0.707 (0.685 to 0.728), miRNA 0.671 (0.657 to 0.685), noise 0.510 (0.470 to 0.549).

BRCA (583 patients)

| Method | AUROC with noise | AUROC without | Loss | 95% interval | Decision |
| --- | --- | --- | --- | --- | --- |
| naive concatenation | 0.695 | 0.935 | 0.240 | 0.205 to 0.262 | fails |
| mogonet_style (re-implementation) | 0.816 | 0.935 | 0.119 | 0.112 to 0.126 | fails |
| late-fusion MLP | 0.893 | 0.917 | 0.023 | 0.016 to 0.030 | inconclusive |
| SGOF | 0.933 | 0.935 | 0.002 | -0.001 to 0.004 | supports reliance (provisional) |

Solo AUROC: mRNA 0.936 (0.933 to 0.938), DNAm 0.796 (0.789 to 0.803), miRNA 0.857 (0.848 to 0.865), noise 0.507 (0.489 to 0.522).

Flags: `layer_not_above_chance` on the noise layer in both datasets (held-out performance does not exceed chance). `gain_only_with_chance_level_layer` was not raised in either dataset (no method gained from the noise layer with an interval below zero). Reports: `reports/rosmap.json`, `reports/brca.json`.

## Check against the SGOF paper

The package reports match the paper at its printed precision (an earlier draft of this table rounded four values twice; they are corrected here). SGOF noise minus real: -0.0062 on ROSMAP and -0.0018 on BRCA (paper -0.006 and -0.002; `reproduce_tables.py` targets -0.0062 and -0.0018). Naive: -0.2060 and -0.2401 (paper -0.206 and -0.240). The additional methods also equal the JSON summary (mogonet_style -0.1835 and -0.1192; late-fusion MLP -0.0257 and -0.0232). Solo means equal the JSON summary (for example ROSMAP noise 0.5096, BRCA mRNA 0.9360). No mismatch found. This is an arithmetic reproduction of the same numbers, not independent confirmation.

## What this does and does not show

It shows that the v0.1.0 layer test, run unchanged on data other than the 111-patient depression cohort, reads a different input shape correctly, reproduces the paper's reported numbers, flags the noise layer as not above chance, and gives the same ordering of methods the paper reports: naive concatenation and the re-implemented MOGONET-style model fail the illustrative limit, SGOF stays within it.

It does not show:

- Anything prospective. These results were already reported in the SGOF paper and the package rules were fixed on the same day as this analysis (PROTOCOL section 5).
- Behavior on a real uninformative clinical layer. The tested layer is synthetic iid noise; the test passing or failing on it says nothing about correlated, partially informative or confounded layers.
- Clinical validity. ROSMAP and BRCA are public research benchmarks, and these are not patient-safety findings.
- Independence. The same author ran the models, the noise injection and this test.
- Narrow intervals as evidence. Intervals are over only 5 repeat means, with repeats sharing patients, and are optimistic about new patients; no out-of-fold predictions exist, so under PROTOCOL section 6 the "supports reliance" decisions are provisional. The SGOF intervals cross zero and sit below 0.02, but an interval from 5 repeats is not a sampling interval.
- Sensitivity to the limit. The late-fusion MLP sits next to the 0.02 limit (ROSMAP fails at 0.021 lower bound, BRCA inconclusive); the decision there depends on an illustrative number.
- Official MOGONET behavior. The "mogonet_style" rows are a re-implementation.
- Dataset terms. The license of the MOGONET-bundled benchmark files is unknown to this package.
