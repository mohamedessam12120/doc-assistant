import sys

import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(
    name="policies", embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

question = " ".join(sys.argv[1:]) or "How many days of annual leave do I get?"
res = collection.query(query_texts=[question], n_results=3)

print("Question:", question)
for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
    print(f"\n[{meta['source']} p.{meta['page']}] distance={dist:.3f}")
    print(doc)