import chromadb
from chromadb.utils import embedding_functions

MISSES = {
    "How many days of annual leave do I get?": "21 working days",
    "How many days of emergency leave are there?": "up to 3 working days per year",
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