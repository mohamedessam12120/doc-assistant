import json
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

# (question, key phrase that must appear in a retrieved chunk)
IN_SCOPE = [
    ("How many days of annual leave do I get?", "21 working days"),
    ("How many leave days after 10 years of service?", "30 working days"),
    ("How early must I request a long leave?", "14 days in advance"),
    ("Can I carry over unused annual leave?", "5 unused annual leave days"),
    ("When do carried-over leave days expire?", "31 March"),
    ("How many paid sick days per year?", "15 days of paid sick leave"),
    ("When do I need a medical certificate?", "more than 2 consecutive days"),
    ("How long is maternity leave?", "90 calendar days"),
    ("When must paternity leave be taken?", "within 30 days of the birth"),
    ("How many days of emergency leave are there?", "up to 3 working days per year"),
    ("How long can unpaid leave be?", "Unpaid leave of up to 30 days"),
    ("What are the standard working hours?", "9:00 to 17:00"),
    ("What are the core hours?", "10:00 to 15:00"),
    ("How is overtime paid?", "1.5 times"),
    ("How many days can I work remotely?", "up to 2 days per week"),
    ("Can I work from home during probation?", "cannot work remotely"),
    ("When must I report a lost device?", "within 24 hours"),
    ("How much is the transport allowance?", "1,500 EGP per month"),
    ("Does health insurance cover my family?", "up to 3 dependents"),
    ("How big is the annual bonus?", "up to one month of salary"),
    ("What is the yearly training budget?", "20,000 EGP per year"),
    ("What is the hotel limit per night when traveling?", "3,000 EGP per night"),
    ("What is the daily meal allowance on trips?", "600 EGP"),
    ("How fast must I submit expense receipts?", "within 10 working days"),
    ("Which expense claims need director approval?", "above 5,000 EGP"),
    ("How much is the mileage reimbursement?", "4 EGP per kilometer"),
]
OUT_OF_SCOPE = [
    "What is the company dress code?",
    "How do I reset my laptop password?",
    "Who is the CEO of the company?",
    "Is there a gym membership benefit?",
]


def norm(s):
    return " ".join(s.lower().split())


client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(
    "policies", embedding_function=embedding_functions.DefaultEmbeddingFunction()
)


def top3(q):
    r = collection.query(query_texts=[q], n_results=3)
    return r["documents"][0], r["distances"][0]


hit1 = hit3 = 0
in_dists, results = [], []
for q, key in IN_SCOPE:
    docs, dists = top3(q)
    found = [norm(key) in norm(d) for d in docs]
    hit1 += found[0]
    hit3 += any(found)
    in_dists.append(dists[0])
    tag = "HIT@1" if found[0] else ("HIT@3" if any(found) else "MISS ")
    print(f"{tag} d={dists[0]:.3f}  {q}")
    results.append({"question": q, "hit1": found[0], "hit3": any(found), "top1_distance": round(dists[0], 3)})

print("\nOut-of-scope questions (should be far away):")
out_dists = []
for q in OUT_OF_SCOPE:
    _, dists = top3(q)
    out_dists.append(dists[0])
    print(f"d={dists[0]:.3f}  {q}")

n = len(IN_SCOPE)
summary = {
    "questions": n,
    "hit_at_1": round(hit1 / n, 3),
    "hit_at_3": round(hit3 / n, 3),
    "in_scope_top1_distance_max": round(max(in_dists), 3),
    "out_of_scope_top1_distance_min": round(min(out_dists), 3),
}
print("\nSUMMARY:", summary)
Path("reports").mkdir(exist_ok=True)
Path("reports/retrieval_eval.json").write_text(json.dumps({"summary": summary, "results": results}, indent=2))