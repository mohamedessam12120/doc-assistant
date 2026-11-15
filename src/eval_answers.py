import json
import re
from pathlib import Path

from ask import NO_ANSWER, ask

# (question, regex that the correct answer must match)
IN_SCOPE = [
    ("How many days of annual leave do I get?", r"\b21\b"),
    ("How many leave days after 10 years of service?", r"\b30\b"),
    ("How early must I request a long leave?", r"\b14\b"),
    ("Can I carry over unused annual leave?", r"\b5\b"),
    ("When do carried-over leave days expire?", r"31 march"),
    ("How many paid sick days per year?", r"\b15\b"),
    ("When do I need a medical certificate?", r"\b2\b"),
    ("How long is maternity leave?", r"\b90\b"),
    ("When must paternity leave be taken?", r"\b30\b"),
    ("How many days of emergency leave are there?", r"\b3\b"),
    ("How long can unpaid leave be?", r"\b30\b"),
    ("What are the standard working hours?", r"\b9(:00)?\b"),
    ("What are the core hours?", r"\b10(:00)?\b"),
    ("How is overtime paid?", r"1\.5"),
    ("How many days can I work remotely?", r"\b2\b"),
    ("Can I work from home during probation?", r"\b(cannot|can't|not|no)\b"),
    ("When must I report a lost device?", r"\b24\b"),
    ("How much is the transport allowance?", r"1,?500"),
    ("Does health insurance cover my family?", r"\b3\b|dependent|yes"),
    ("How big is the annual bonus?", r"one month|1 month|\bmonth\b"),
    ("What is the yearly training budget?", r"20,?000"),
    ("What is the hotel limit per night when traveling?", r"3,?000"),
    ("What is the daily meal allowance on trips?", r"\b600\b"),
    ("How fast must I submit expense receipts?", r"\b10\b"),
    ("Which expense claims need director approval?", r"5,?000"),
    ("How much is the mileage reimbursement?", r"\b4\b"),
]
OUT_OF_SCOPE = [
    "What is the company dress code?",
    "How do I reset my laptop password?",
    "Who is the CEO of the company?",
    "Is there a gym membership benefit?",
]

correct, results = 0, []
for q, pattern in IN_SCOPE:
    answer, _ = ask(q)
    ok = bool(re.search(pattern, answer.lower())) and answer != NO_ANSWER
    correct += ok
    results.append({"question": q, "answer": answer, "correct": ok})
    print(("OK   " if ok else "FAIL ") + q + "\n      -> " + answer.replace("\n", " ")[:160])

refused = 0
print("\nOut-of-scope (should say I don't know):")
for q in OUT_OF_SCOPE:
    answer, _ = ask(q)
    ok = answer.strip().lower().startswith("i don't know")
    refused += ok
    results.append({"question": q, "answer": answer, "refused": ok})
    print(("OK   " if ok else "FAIL ") + q + "\n      -> " + answer.replace("\n", " ")[:160])

summary = {
    "in_scope_correct": f"{correct}/{len(IN_SCOPE)}",
    "out_of_scope_refused": f"{refused}/{len(OUT_OF_SCOPE)}",
}
print("\nSUMMARY:", summary)
Path("reports").mkdir(exist_ok=True)
Path("reports/answer_eval.json").write_text(json.dumps({"summary": summary, "results": results}, indent=2))