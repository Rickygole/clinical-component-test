import csv
from pathlib import Path

import numpy as np

from cctest import layers
from checks import check, finish

DATA = Path(__file__).resolve().parent.parent / "data" / "sgof2026"
TABLE2 = {
    "naive_concatenation": ("0.331", "0.675", "0.343"),
    "attention_fusion": ("0.356", "0.660", "0.304"),
    "equal_weight_fusion": ("0.373", "0.658", "0.285"),
    "mogonet": ("0.502", "0.676", "0.174"),
    "similarity_network_fusion": ("0.532", "0.644", "0.112"),
    "late_fusion": ("0.619", "0.702", "0.083"),
    "gradient_boosted_trees": ("0.591", "0.647", "0.057"),
    "mogcn": ("0.556", "0.588", "0.032"),
}
ROUNDED = ("stored out-of-fold probabilities were rounded to six decimals when saved, "
           "which creates tied scores; the paper value used the unrounded probabilities")

r = layers.run(DATA / "fold_auroc.csv", DATA / "oof_predictions.csv")
loss = {e["components"][0]: e for e in r["entries"] if e["test"] == "auroc_loss_from_adding_layer"}
solo = {tuple(e["components"]): e for e in r["entries"] if e["test"] == "solo_layer_auroc"}

print("SGOF, BIBM 2026 workshop, Tables I and II and Section IV\n")
for m, (w, wo, g) in TABLE2.items():
    check(f"{m}: AUROC with genotype", loss[m]["auroc_with"], w)
    check(f"{m}: AUROC without genotype", loss[m]["auroc_without"], wo)
    check(f"{m}: loss from adding genotype", loss[m]["estimate"], g)
drops = [loss[m]["estimate"] for m in TABLE2]
check("all eight conventional methods lose AUROC (count)", sum(d > 0 for d in drops), "8")

s = loss["sgof"]
check("SGOF: AUROC with genotype", s["auroc_with"], "0.671")
check("SGOF: AUROC without genotype", s["auroc_without"], "0.674")
check("SGOF: change from adding genotype", s["auroc_change_with_minus_without"], "-0.003")
check("SGOF: change, repeat interval lower", -s["repeat_upper_95"], "-0.010")
check("SGOF: change, repeat interval upper", -s["repeat_lower_95"], "0.005")
check("SGOF: change, patient interval lower", -s["patient_upper_95"], "-0.012", known_difference=ROUNDED)
check("SGOF: change, patient interval upper", -s["patient_lower_95"], "0.012", known_difference=ROUNDED)
check("SGOF earlier run: change from adding genotype", loss["sgof_earlier_run"]["auroc_change_with_minus_without"], "-0.012")
v = loss["validation_weighted_ensemble"]
check("validation weighted ensemble: AUROC with genotype", v["auroc_with"], "0.706")
check("validation weighted ensemble: AUROC without genotype", v["auroc_without"], "0.712")
check("validation weighted ensemble: change", v["auroc_change_with_minus_without"], "-0.007")
check("validation weighted ensemble: interval excludes zero (1 = yes)", float(v["repeat_lower_95"] > 0), "1")

for fam, m, e, g in (("lr_single_layer", "0.691", "0.650", "0.306"), ("gcn_single_layer", "0.669", "0.607", "0.355")):
    check(f"{fam}: methylation alone", solo[(fam, "methylation")]["estimate"], m)
    check(f"{fam}: expression alone", solo[(fam, "expression")]["estimate"], e)
    check(f"{fam}: genotype alone", solo[(fam, "genotype")]["estimate"], g)
null = [float(x["mean_fold_auroc"]) for x in csv.DictReader(open(DATA / "single_layer_permutation_null.csv")) if x["layer"] == "genotype"]
check("genotype GCN permutation null, 2.5th percentile", np.percentile(null, 2.5), "0.30")
check("genotype GCN permutation null, 97.5th percentile", np.percentile(null, 97.5), "0.69")
flagged = sorted(f["components"][0] for f in r["flags"] if f["flag"] == "layer_not_above_chance")
check("layers flagged 'held-out performance does not exceed chance' (genotype only = 1)", float(flagged == ["genotype"]), "1")
finish("reproduce_sgof")
