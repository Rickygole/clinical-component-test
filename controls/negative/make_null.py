import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor

import numpy as np

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
R = 200
MID = "llama3_8b,qwen25_7b,gemma3n_e4b"
ICDM = "data/icdm2026/"
HELM = "outside/data/helm_lite_medqa_answers.csv"
CONFIGS = [
    ("medqa3_mid", ICDM + "medqa_answers.csv", MID),
    ("medqa4_deepseek", ICDM + "medqa_answers.csv", MID + ",deepseek_v3"),
    ("medqa4_gpt4o", ICDM + "medqa_answers.csv", MID + ",gpt4o"),
    ("medqa5_all", ICDM + "medqa_answers.csv", MID + ",deepseek_v3,gpt4o"),
    ("medmcqa4_gpt4o", ICDM + "medmcqa_answers.csv", MID + ",gpt4o"),
    (
        "helm_A",
        HELM,
        "meta_llama-3.1-8b-instruct-turbo,qwen_qwen2.5-7b-instruct-turbo,google_gemma-2-9b-it,"
        "openai_gpt-4o-mini-2024-07-18,mistralai_mistral-7b-instruct-v0.3",
    ),
    (
        "helm_B",
        HELM,
        "meta_llama-3.1-405b-instruct-turbo,qwen_qwen2.5-72b-instruct-turbo,google_gemini-1.5-pro-002,"
        "deepseek-ai_deepseek-v3,openai_gpt-4o-2024-08-06",
    ),
]


def seed_for(config_index, replicate):
    return 100000 * (config_index + 1) + replicate


def read_rows(path, models):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = [r for r in reader if r["model_id"].strip() in models]
    return fields, rows


def is_valid(row):
    k = int(row["n_options"])
    return row["answer"].strip().upper() in LETTERS[:k] and row["reference_answer"].strip().upper() in LETTERS[:k]


def is_wrong(row):
    return is_valid(row) and row["answer"].strip().upper() != row["reference_answer"].strip().upper()


def wrong_counts(rows, models):
    out = {m: {} for m in models}
    for r in rows:
        if is_wrong(r):
            d = out[r["model_id"].strip()]
            a = r["answer"].strip().upper()
            d[a] = d.get(a, 0) + 1
    return out


def make_replicate(rows, counts, seed):
    rng = np.random.default_rng(seed)
    out = []
    for r in rows:
        r = dict(r)
        if is_wrong(r):
            gold = r["reference_answer"].strip().upper()
            opts = [l for l in LETTERS[: int(r["n_options"])] if l != gold]
            d = counts[r["model_id"].strip()]
            w = np.array([d.get(l, 0) for l in opts], dtype=float)
            w = w / w.sum() if w.sum() else np.full(len(opts), 1.0 / len(opts))
            r["answer"] = opts[rng.choice(len(opts), p=w)]
        out.append(r)
    return out


def check_replicate(rows, new):
    for a, b in zip(rows, new):
        assert a["case_id"] == b["case_id"] and a["model_id"] == b["model_id"]
        assert is_wrong(a) == is_wrong(b)
        assert is_valid(a) == is_valid(b)
        if not is_wrong(a):
            assert a["answer"] == b["answer"]
        else:
            assert b["answer"].strip().upper() != a["reference_answer"].strip().upper()
            assert b["answer"] in LETTERS[: int(a["n_options"])]


def write_csv(path, fields, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def run_cctest(cctest, csv_path, models, report_path):
    p = subprocess.run(
        [cctest, "agreement", csv_path, "--models", models, "--out", report_path],
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    with open(report_path) as f:
        rep = json.load(f)
    e = next(x for x in rep["entries"] if x["test"] == "unanimous_wrong_rate")
    flag = int(any(x["flag"] == "convergent_failure" for x in rep["flags"]))
    return [e["count"], e["denominator"], e["estimate"], e["baselines"]["permutation_95th_percentile"], flag]


def job(args):
    ci, replicate, cctest, root, outdir = args
    name, path, models = CONFIGS[ci]
    mlist = [m.strip() for m in models.split(",")]
    fields, rows = read_rows(os.path.join(root, path), set(mlist))
    with tempfile.TemporaryDirectory() as tmp:
        report_path = os.path.join(tmp, "report.json")
        if replicate == 0:
            seed = "NA"
            res = run_cctest(cctest, os.path.join(root, path), models, report_path)
        else:
            seed = seed_for(ci, replicate)
            new = make_replicate(rows, wrong_counts(rows, mlist), seed)
            check_replicate(rows, new)
            csv_path = os.path.join(tmp, "replicate.csv")
            write_csv(csv_path, fields, new)
            res = run_cctest(cctest, csv_path, models, report_path)
        if replicate in (0, 1):
            tag = "real" if replicate == 0 else "null_replicate_1"
            with open(report_path) as f:
                text = f.read()
            with open(os.path.join(outdir, "examples", f"{name}__{tag}.json"), "w") as f:
                f.write(text)
    return [name, replicate, seed] + res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cctest", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--replicates", type=int, default=R)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.outdir, "examples"), exist_ok=True)
    jobs = [
        (ci, r, a.cctest, a.root, a.outdir)
        for ci, c in enumerate(CONFIGS)
        if a.only is None or c[0] == a.only
        for r in range(0, a.replicates + 1)
    ]
    with ProcessPoolExecutor(a.workers) as ex:
        results = list(ex.map(job, jobs, chunksize=1))
    header = ["configuration", "replicate", "seed", "unanimous_wrong_count", "all_wrong_count",
              "unanimous_wrong_rate", "permutation_95th_percentile", "flag"]
    for fname, keep in (("replicates_v0.1.2.tsv", lambda r: r[1] > 0), ("real_data_v0.1.2.tsv", lambda r: r[1] == 0)):
        with open(os.path.join(a.outdir, fname), "w") as f:
            f.write("\t".join(header) + "\n")
            for r in results:
                if keep(r):
                    f.write("\t".join(repr(x) if isinstance(x, float) else str(x) for x in r) + "\n")


if __name__ == "__main__":
    sys.exit(main())
