import csv
import json
import sys
from pathlib import Path

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DEVELOPER = {"meta": "Meta", "qwen": "Alibaba", "google": "Google", "openai": "OpenAI",
             "mistralai": "Mistral AI", "deepseek-ai": "DeepSeek"}


def stat_value(stats, names):
    for s in stats:
        if s.get("name", {}).get("name") in names and not s.get("name", {}).get("perturbation"):
            return s.get("mean", s.get("sum")), s["name"]["name"]
    return None, None


def extract(model_dir):
    model = model_dir.name
    instances = json.loads((model_dir / "instances.json").read_text())
    preds = {p["instance_id"]: p for p in json.loads((model_dir / "display_predictions.json").read_text())}
    stats = {s["instance_id"]: s["stats"] for s in json.loads((model_dir / "per_instance_stats.json").read_text())}
    rows, disagree, missing, used = [], 0, 0, set()
    for inst in instances:
        refs = inst["references"]
        gold = [LETTERS[i] for i, r in enumerate(refs) if "correct" in r["tags"]]
        if len(gold) != 1:
            raise SystemExit(f"{model} {inst['id']}: {len(gold)} correct references")
        p = preds[inst["id"]]
        text = p["predicted_text"].strip()
        answer = text[0] if text and text[0] in LETTERS[:len(refs)] else ""
        helm, name = stat_value(stats.get(inst["id"], []), ("exact_match",))
        if helm is None:
            missing += 1
        else:
            used.add(name)
            if int(round(helm)) != int(answer == gold[0]):
                disagree += 1
        rows.append([inst["id"], model, DEVELOPER[model.split("_")[0]], answer, gold[0], len(refs)])
    return rows, disagree, missing, used


def main(raw, out):
    all_rows = []
    for d in sorted(p for p in Path(raw).iterdir() if p.is_dir()):
        rows, disagree, missing, used = extract(d)
        acc = sum(r[3] == r[4] for r in rows) / len(rows)
        print(f"{d.name}: {len(rows)} instances, accuracy {acc:.3f}, unscored {sum(r[3] == '' for r in rows)}, "
              f"disagreements with HELM {disagree}, missing HELM statistic {missing} ({', '.join(sorted(used))})")
        all_rows += rows
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "model_id", "developer", "answer", "reference_answer", "n_options"])
        w.writerows(all_rows)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
