# Commands for the v0.1.2 negative control

Run from the repository root. `cctest` is the v0.1.0 release in its own virtual environment, installed with `pip install git+https://github.com/Rickygole/clinical-component-test@v0.1.0`. Only numpy, scipy and the standard library are used by make_null.py.

Plan commit (made and pushed before any replicate was generated):

    git add controls/negative/PLAN_v0.1.2.md controls/negative/make_null.py
    git commit -m "Plan the v0.1.2 negative control before running it"
    git push

Full run, 7 configurations, replicate 0 (real data) and replicates 1 to 200 each, 8 worker processes. `<cctest>` is the path of the v0.1.0 executable:

    python3 -I controls/negative/make_null.py --cctest <cctest> --root . --outdir controls/negative --workers 8

This writes controls/negative/replicates_v0.1.2.tsv (1,400 rows), controls/negative/real_data_v0.1.2.tsv (7 rows) and controls/negative/examples/ (the report of replicate 1 and of the real data for each configuration).

Each run inside the script is equivalent to, with defaults of 10,000 permutations and seed 42:

    cctest agreement <csv> --models <list> --out <report>

where `<csv>` is the real file (replicate 0) or the replicate file written to a temporary folder (replicates 1 to 200, seed 100000 * i + r for configuration i and replicate r). The model lists and file paths are in make_null.py.

Options of make_null.py not used for the reported run: `--replicates` and `--only` (one configuration).

Flag rates and Wilson intervals in RESULTS_v0.1.2.md were first computed with inline Python. The same table is reproduced by the shipped script, run with the v0.1.0 install:

    python controls/negative/summarize.py controls/negative/replicates_v0.1.2.tsv

The Wilson interval is the score interval with z = 1.959964, the same form as cctest's own intervals.
