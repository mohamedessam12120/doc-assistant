from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

DOCS_DIR = Path("docs")
DB_PATH = "chroma_db"
COLLECTION = "policies"
CHUNK_SIZE = 400   # characters
OVERLAP = 80       # characters shared between neighbor chunks


def chunk_text(text, size=CHUNK_SIZE, overlap=OVERLAP):
    text = " ".join(text.split())
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = text.rfind(". ", start, end)  # prefer to end at a sentence
            if cut > start + size // 2:
                end = cut + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
        nxt = text.find(" ", start)  # move to the next word boundary
        start = min(nxt + 1, end) if nxt != -1 else end
        return chunks


def main():
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        client.delete_collection(COLLECTION)  # rebuild from scratch each run
    except Exception:
        pass
    ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=COLLECTION, embedding_function=ef, metadata={"hnsw:space": "cosine"}
    )

    ids, texts, metas = [], [], []
    pdfs = sorted(DOCS_DIR.glob("*.pdf"))
    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page_no, page in enumerate(reader.pages, start=1):
            for i, chunk in enumerate(chunk_text(page.extract_text() or "")):
                ids.append(f"{pdf.stem}-p{page_no}-c{i}")
                texts.append(chunk)
                metas.append({"source": pdf.name, "page": page_no})

    collection.add(ids=ids, documents=texts, metadatas=metas)
    print(f"PDFs: {len(pdfs)} | chunks: {len(texts)}")
    print("--- sample chunk ---")
    print(metas[0], "\n" + texts[0])


if __name__ == "__main__":
    main()