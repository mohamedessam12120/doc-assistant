import sys

import chromadb
import ollama
from chromadb.utils import embedding_functions

MODEL = "llama3.2:3b"
TOP_K = 5
MAX_DISTANCE = 0.71  # tentative, based on our 26-question set (in-scope <= 0.67, out-of-scope >= 0.755)
NO_ANSWER = "I don't know based on the provided documents."

SYSTEM = (
    "You are an HR policy assistant. Answer ONLY with facts that are explicitly stated in the context. "
    "Do not infer, guess, or answer 'No' just because something is not mentioned. "
    "Be short and give the exact numbers. "
    f"If the context does not explicitly contain the answer, reply exactly: {NO_ANSWER}"
)

collection = chromadb.PersistentClient(path="chroma_db").get_collection(
    "policies", embedding_function=embedding_functions.DefaultEmbeddingFunction()
)


def ask_detailed(question):
    res = collection.query(query_texts=[question], n_results=TOP_K)
    docs, metas, dists = res["documents"][0], res["metadatas"][0], res["distances"][0]
    top_distance = round(dists[0], 3)

    # Gate: if even the best chunk is far from the question, do not call the LLM
    if dists[0] > MAX_DISTANCE:
        return {"answer": NO_ANSWER, "sources": [], "top_distance": top_distance, "refused": True}

    context = "\n\n".join(f"[{m['source']} p.{m['page']}]\n{d}" for d, m in zip(docs, metas))
    reply = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        options={"temperature": 0},
    )
    answer = reply["message"]["content"]
    refused = answer.strip().lower().startswith("i don't know")
    # Show only the 2 closest chunks as sources, not all 5
    sources = [] if refused else [{"source": m["source"], "page": m["page"]} for m in metas[:2]]
    return {"answer": answer, "sources": sources, "top_distance": top_distance, "refused": refused}


def ask(question):
    r = ask_detailed(question)
    return r["answer"], [f"{s['source']} p.{s['page']}" for s in r["sources"]]


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How many days of annual leave do I get?"
    answer, sources = ask(question)
    print("Q:", question)
    print("A:", answer)
    print("Retrieved from:", ", ".join(sources) if sources else "-")