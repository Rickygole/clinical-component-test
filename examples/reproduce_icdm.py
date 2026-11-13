from pathlib import Path

from cctest import agreement
from checks import check, finish

DATA = Path(__file__).resolve().parent.parent / "data" / "icdm2026"
MID = ["llama3_8b", "qwen25_7b", "gemma3n_e4b"]


def run(ds, models):
    r = agreement.run(DATA / f"{ds}_answers.csv", models)
    e = {x["test"]: x for x in r["entries"]}
    return e, e["unanimous_wrong_rate"]["baselines"], r["flags"]


print("ICDM 2026, Table I and Section V-A")
print("Table I caption: the chance column is the empirical value for the two k = 4 rows with distinct frontier models and naive chance for the other rows\n")
e, b, f = run("medqa", MID + ["deepseek_v3", "gpt4o"])
u = e["unanimous_wrong_rate"]
check("MedQA 5 models: all-wrong cases", u["denominator"], "57")
check("MedQA 5 models: unanimous wrong cases", u["count"], "14")
check("MedQA 5 models: unanimous wrong rate (%)", u["estimate"], "24.6", 100)
check("MedQA 5 models: Wilson lower (%)", u["lower_95"], "15.2", 100)
check("MedQA 5 models: Wilson upper (%)", u["upper_95"], "37.1", 100)
check("MedQA 5 models: chance column, naive (%)", b["naive_independence"], "1.23", 100)
check("MedQA 5 models: ratio to naive chance", b["ratio_to_naive"], "19.9")
check("MedQA 5 models: agreed wrong exposure (%)", e["agreed_wrong_exposure"]["estimate"], "1.1", 100)

e, b, f = run("medqa", MID)
u = e["unanimous_wrong_rate"]
check("MedQA 3 mid tier: all-wrong cases", u["denominator"], "279")
check("MedQA 3 mid tier: unanimous wrong cases", u["count"], "117")
check("MedQA 3 mid tier: unanimous wrong rate (%)", u["estimate"], "41.9", 100)
check("MedQA 3 mid tier: chance column, naive (%)", b["naive_independence"], "11.1", 100)
check("MedQA 3 mid tier: ratio to chance", b["ratio_to_naive"], "3.8")
check("MedQA 3 mid tier: agreed wrong exposure (%)", e["agreed_wrong_exposure"]["estimate"], "9.2", 100)
check("MedQA 3 mid tier: agreed cases", e["agreed_answer_error_rate"]["denominator"], "520")
check("MedQA 3 mid tier: error rate among agreed answers (%)", e["agreed_answer_error_rate"]["estimate"], "22.5", 100)

e, b, f = run("medqa", MID + ["deepseek_v3"])
u = e["unanimous_wrong_rate"]
check("MedQA 4 incl. DeepSeek-V3: all-wrong cases", u["denominator"], "143")
check("MedQA 4 incl. DeepSeek-V3: unanimous wrong cases", u["count"], "48")
check("MedQA 4 incl. DeepSeek-V3: unanimous wrong rate (%)", u["estimate"], "33.6", 100)
check("MedQA 4 incl. DeepSeek-V3: Wilson lower (%)", u["lower_95"], "26.3", 100)
check("MedQA 4 incl. DeepSeek-V3: Wilson upper (%)", u["upper_95"], "41.6", 100)
check("MedQA 4 incl. DeepSeek-V3: chance column, model expectation (%)", b["model_expectation"], "3.9", 100)
check("MedQA 4 incl. DeepSeek-V3: ratio", b["ratio_to_model_expectation"], "8.6")
check("MedQA 4 incl. DeepSeek-V3: agreed wrong exposure (%)", e["agreed_wrong_exposure"]["estimate"], "3.8", 100)

e, b, f = run("medqa", MID + ["gpt4o"])
check("MedQA 4 incl. GPT-4o: unanimous wrong rate (%)", e["unanimous_wrong_rate"]["estimate"], "26.0", 100)
check("MedQA 4 incl. GPT-4o: chance column, naive (%)", b["naive_independence"], "3.7", 100)
check("MedQA 4 incl. GPT-4o: ratio", b["ratio_to_naive"], "7.0")

e, b, f = run("medmcqa", MID + ["gpt4o"])
u = e["unanimous_wrong_rate"]
check("MedMCQA 4 incl. GPT-4o: all-wrong cases", u["denominator"], "301")
check("MedMCQA 4 incl. GPT-4o: unanimous wrong cases", u["count"], "71")
check("MedMCQA 4 incl. GPT-4o: unanimous wrong rate (%)", u["estimate"], "23.6", 100)
check("MedMCQA 4 incl. GPT-4o: Wilson lower (%)", u["lower_95"], "19.1", 100)
check("MedMCQA 4 incl. GPT-4o: Wilson upper (%)", u["upper_95"], "28.7", 100)
check("MedMCQA 4 incl. GPT-4o: chance column, model expectation (%)", b["model_expectation"], "4.2", 100)
check("MedMCQA 4 incl. GPT-4o: ratio", b["ratio_to_model_expectation"], "5.7")
check("MedMCQA 4 incl. GPT-4o: agreed wrong exposure (%)", e["agreed_wrong_exposure"]["estimate"], "2.5", 100)

finish("reproduce_icdm")
