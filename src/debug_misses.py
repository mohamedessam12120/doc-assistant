import chromadb
from chromadb.utils import embedding_functions

MISSES = {
    "Can I carry over unused annual leave?": "5 unused annual leave days",
    "When do carried-over leave days expire?": "31 March",
    "How many paid sick days per year?": "15 days of paid sick leave",
    "When do I need a medical certificate?": "more than 2 consecutive days",
    "How long can unpaid leave be?": "Unpaid leave of up to 30 days",
    "How is overtime paid?": "1.5 times",
    "When must I report a lost device?": "within 24 hours",
    "What is the yearly training budget?": "20,000 EGP per year",
    "What is the daily meal allowance on trips?": "600 EGP",
    "How much is the mileage reimbursement?": "4 EGP per kilometer",
}


def norm(s):
    return " ".join(s.lower().split())


client = chromadb.PersistentClient(path="chroma_db")
col = client.get_collection(
    "policies", embedding_function=embedding_functions.DefaultEmbeddingFunction()
)
allc = col.get(include=["documents"])
chunks = dict(zip(allc["ids"], allc["documents"]))
print("total chunks:", len(chunks))

for q, key in MISSES.items():
    holders = [i for i, d in chunks.items() if norm(key) in norm(d)]
    ranked = col.query(query_texts=[q], n_results=10)["ids"][0]
    print("\nQ:", q)
    print("  key:", key)
    if not holders:
        print("  -> key is NOT inside any single chunk (split across chunks)")
    for h in holders:
        rank = ranked.index(h) + 1 if h in ranked else ">10"
        print(f"  -> key is in chunk {h}, its rank in search: {rank}")
    print("  top1 chunk:", ranked[0])