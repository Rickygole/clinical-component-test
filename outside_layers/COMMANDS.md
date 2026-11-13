# Commands

Run from the package root, `clinical-component-test`. The CLI is the unchanged v0.1.0 build installed in a separate virtual environment. Seed is the default, 2026.

    python3 outside_layers/export_public.py
    cctest layers outside_layers/data/rosmap_fold_auroc.csv --limits examples/limits_example.json --out outside_layers/reports/rosmap.json
    cctest layers outside_layers/data/brca_fold_auroc.csv --limits examples/limits_example.json --out outside_layers/reports/brca.json

The export script reads `~/sgof-camera-ready/results/public/public_rosmap.json` and `public_brca.json` (hardcoded home-relative path, JSON only) and writes the two fold CSVs. No out-of-fold file is passed because none exists, so every interval is over repeat means.

SHA-256 of the sources and exports:

    2c48017b81ae5154f33eac7a2b530dc1a4a9029eec6c0f3d10cc860297a21011  public_rosmap.json
    3126b8fa902c9c501dab9929e73afe607c23c8c5d0555f34d6c7f4428978c2b7  public_brca.json
    4bdef80e3f07162d6c71ce1146e73b6aaf339cd5278328590e8be0ff0542fa79  data/rosmap_fold_auroc.csv
    adb6f7a378bbc4e3390002f3661c45ce952426ab80fb375a1aee5244697a71a8  data/brca_fold_auroc.csv
