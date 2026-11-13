import csv
import math

import numpy as np
import pytest

from cctest import agreement, layers
from cctest.agreement import InputError
from cctest.report import auroc, decide, denominator_needed, wilson

HEAD = ["case_id", "model_id", "developer", "answer", "reference_answer", "n_options"]


def write(tmp_path, rows, name="a.csv", head=HEAD):
    p = tmp_path / name
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)
    return p


def panel(answers, refs):
    return [[f"c{i}", m, "x", a, refs[i], 4] for i, row in enumerate(answers) for m, a in zip("abc", row)]


@pytest.mark.parametrize("x,n,lo,hi", [(0, 10, 0.0, 0.27753), (10, 10, 0.72247, 1.0), (14, 57, 0.15233, 0.37102), (5, 10, 0.23659, 0.76341)])
def test_wilson_reference_values(x, n, lo, hi):
    _, l, h = wilson(x, n)
    assert l == pytest.approx(lo, abs=1e-5) and h == pytest.approx(hi, abs=1e-5)


def test_wilson_empty_denominator():
    assert all(math.isnan(v) for v in wilson(0, 0))


def test_auroc_known_value_and_ties():
    assert auroc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]) == 0.75
    assert auroc([0, 1], [0.5, 0.5]) == 0.5
    assert math.isnan(auroc([1, 1], [0.2, 0.3]))


def test_decision_rule_three_outcomes():
    assert decide(0.01, 0.04, 0.05) == "supports reliance"
    assert decide(0.06, 0.09, 0.05) == "fails"
    assert decide(0.03, 0.08, 0.05) == "inconclusive"
    assert decide(0.03, 0.08, None) == "no limit recorded"


def test_denominator_needed_resolves_interval():
    m = denominator_needed(3, 100, 0.05)
    assert m is not None and m > 100
    assert wilson(0.03 * m, m)[2] <= 0.05
    assert wilson(0.03 * (m - 1), m - 1)[2] > 0.05


def test_agreement_hand_computed(tmp_path):
    answers = [("A", "A", "A"), ("B", "B", "B"), ("B", "C", "D"), ("C", "C", "C"), ("A", "B", "C"), ("D", "D", "B")]
    refs = ["A", "A", "A", "A", "A", "A"]
    r = agreement.run(write(tmp_path, panel(answers, refs)), list("abc"), n_perm=200)
    e = {x["test"]: x for x in r["entries"]}
    assert (e["agreed_answer_error_rate"]["count"], e["agreed_answer_error_rate"]["denominator"]) == (2, 3)
    assert (e["unanimous_wrong_rate"]["count"], e["unanimous_wrong_rate"]["denominator"]) == (2, 4)
    assert (e["agreed_wrong_exposure"]["count"], e["agreed_wrong_exposure"]["denominator"]) == (2, 6)
    assert e["unanimous_wrong_rate"]["baselines"]["naive_independence"] == pytest.approx(1 / 9)


def test_zero_event_case(tmp_path):
    answers = [("A", "A", "A")] * 5
    r = agreement.run(write(tmp_path, panel(answers, ["A"] * 5)), list("abc"), n_perm=50)
    u = r["entries"][1]
    assert u["denominator"] == 0 and u["estimate"] is None and r["flags"] == []
    assert r["entries"][0]["count"] == 0 and r["entries"][0]["upper_95"] == pytest.approx(0.43448, abs=1e-5)


def test_all_wrong_same_answer_flags(tmp_path):
    refs = ["A"] * 30
    answers = [("BCD"[i % 3],) * 3 for i in range(30)]
    r = agreement.run(write(tmp_path, panel(answers, refs)), list("abc"), n_perm=200)
    assert r["entries"][1]["estimate"] == 1.0
    assert [f["flag"] for f in r["flags"]] == ["convergent_failure"]


def test_independent_errors_do_not_flag(tmp_path):
    rng = np.random.default_rng(7)
    refs = rng.choice(list("ABCD"), 3000)
    rows = []
    for i, g in enumerate(refs):
        for m in "abc":
            wrong = [l for l in "ABCD" if l != g]
            a = g if rng.random() < 0.5 else rng.choice(wrong)
            rows.append([f"c{i}", m, "x", a, g, 4])
    r = agreement.run(write(tmp_path, rows), list("abc"), n_perm=500)
    assert r["flags"] == []
    assert r["entries"][1]["estimate"] == pytest.approx(1 / 9, abs=0.04)


def test_missing_answer_is_logged_not_dropped(tmp_path):
    rows = panel([("A", "", "A"), ("B", "B", "B")], ["A", "A"])
    r = agreement.run(write(tmp_path, rows), list("abc"), n_perm=20)
    assert r["entries"][2]["denominator"] == 1
    assert r["notes"][0].startswith("1 of 2 cases unscored")


def test_duplicate_rows_rejected(tmp_path):
    rows = panel([("A", "A", "A")], ["A"])
    with pytest.raises(InputError, match="duplicated"):
        agreement.run(write(tmp_path, rows + rows[:1]), list("abc"))


def test_unequal_coverage_rejected(tmp_path):
    rows = panel([("A", "A", "A"), ("B", "B", "B")], ["A", "A"])[:-1]
    with pytest.raises(InputError, match="unequal coverage"):
        agreement.run(write(tmp_path, rows), list("abc"))


def folds(tmp_path, with_shift, solo_level):
    rows = []
    rng = np.random.default_rng(0)
    for r in range(4):
        for k in range(5):
            base = 0.7 + rng.normal(0, 0.01)
            rows.append(["m", "noise", "without", r, k, base])
            rows.append(["m", "noise", "with", r, k, base + with_shift])
            rows.append(["solo", "noise", "solo", r, k, solo_level + rng.normal(0, 0.01)])
    return write(tmp_path, rows, "f.csv", ["model_id", "layer", "condition", "repeat", "fold", "auroc"])


def test_layer_loss_is_exact_and_chance_layer_flagged(tmp_path):
    r = layers.run(folds(tmp_path, -0.1, 0.45), b=500)
    e = [x for x in r["entries"] if x["test"] == "auroc_loss_from_adding_layer"][0]
    assert e["estimate"] == pytest.approx(0.1) and e["lower_95"] == pytest.approx(0.1)
    assert [f["flag"] for f in r["flags"]] == ["layer_not_above_chance"]


def test_gain_only_with_chance_layer_flagged(tmp_path):
    r = layers.run(folds(tmp_path, 0.05, 0.45), b=500)
    assert {f["flag"] for f in r["flags"]} == {"layer_not_above_chance", "gain_only_with_chance_level_layer"}


def test_informative_layer_not_flagged(tmp_path):
    r = layers.run(folds(tmp_path, 0.02, 0.65), b=500)
    assert r["flags"] == []


def test_layers_reject_unmatched_condition(tmp_path):
    p = write(tmp_path, [["m", "g", "with", 0, 0, 0.6]], "f.csv", ["model_id", "layer", "condition", "repeat", "fold", "auroc"])
    with pytest.raises(InputError, match="no matching 'without'"):
        layers.run(p, b=10)


def test_shared_letter_preference_is_not_flagged(tmp_path):
    refs = list("ABCD") * 8
    answers = [("B" if g == "A" else "A",) * 3 for g in refs]
    r = agreement.run(write(tmp_path, panel(answers, refs)), list("abc"), n_perm=200)
    assert r["entries"][1]["estimate"] == 1.0 and r["flags"] == []


def oof_file(tmp_path, labels_by_repeat, reps=(0, 1)):
    rows = []
    for r, labs in zip(reps, labels_by_repeat):
        for i, lab in enumerate(labs):
            for cond in ("with", "without"):
                rows.append(["m", "noise", cond, r, f"p{i}", 0.2 + 0.6 * (i % 2), lab])
    return write(tmp_path, rows, "o.csv", ["model_id", "layer", "condition", "repeat", "patient_id", "probability", "label"])


def fold_file(tmp_path, with_reps=(0, 1), without_reps=(0, 1), value="0.7"):
    rows = [["m", "noise", "with", r, k, value] for r in with_reps for k in range(2)]
    rows += [["m", "noise", "without", r, k, "0.7"] for r in without_reps for k in range(2)]
    return write(tmp_path, rows, "f.csv", ["model_id", "layer", "condition", "repeat", "fold", "auroc"])


def test_labels_differing_across_repeats_rejected(tmp_path):
    with pytest.raises(InputError, match="differs across repeats"):
        layers.run(fold_file(tmp_path), oof_file(tmp_path, [[0, 1, 0, 1], [1, 0, 0, 1]]), b=10, b_patient=10)


def test_labels_not_binary_rejected(tmp_path):
    with pytest.raises(InputError, match="0 or 1"):
        layers.run(fold_file(tmp_path), oof_file(tmp_path, [[-1, 1, -1, 1]] * 2), b=10, b_patient=10)


def test_misaligned_repeat_ids_rejected(tmp_path):
    with pytest.raises(InputError, match="same repeat and fold ids"):
        layers.run(fold_file(tmp_path, with_reps=(0, 1), without_reps=(1, 2)), b=10)


@pytest.mark.parametrize("value", ["nan", "1.7", "high"])
def test_bad_auroc_values_rejected(tmp_path, value):
    with pytest.raises(InputError):
        layers.run(fold_file(tmp_path, value=value), b=10)


@pytest.mark.parametrize("k", ["-1", "1", "27", "four"])
def test_bad_n_options_rejected(tmp_path, k):
    rows = [["c0", m, "x", "A", "B", k] for m in "abc"]
    with pytest.raises(InputError, match="n_options"):
        agreement.run(write(tmp_path, rows), list("abc"))


def test_lowercase_answers_are_normalised(tmp_path):
    rows = [[f"c{i}", m, "x", "b", "A", 4] for i in range(3) for m in "abc"]
    r = agreement.run(write(tmp_path, rows), list("abc"), n_perm=20)
    assert r["entries"][1]["count"] == 3


@pytest.mark.parametrize("models", [["a", "a"], ["a"]])
def test_duplicate_or_single_model_rejected(tmp_path, models):
    with pytest.raises(InputError, match="two distinct"):
        agreement.run(write(tmp_path, panel([("A", "A", "A")], ["A"])), models)


def test_cli_missing_file_exits_cleanly(tmp_path, capsys):
    from cctest.cli import main
    assert main(["agreement", str(tmp_path / "missing.csv"), "--models", "a,b"]) == 2
    assert "input rejected" in capsys.readouterr().err


def test_empty_denominator_with_limit_is_not_estimable():
    assert decide(float("nan"), float("nan"), 0.1) == "not estimable (empty denominator)"
