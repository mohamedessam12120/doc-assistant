# Company Policy Assistant (RAG)

Question answering over HR policy PDFs. Employees ask in natural language and get an
answer with its source (document and page). If the answer is not in the documents,
the assistant says it does not know instead of guessing.

Runs fully locally: ChromaDB for retrieval, Ollama (`llama3.2:3b`) for answers,
FastAPI for the service, Docker for packaging. All documents are fictional.

## How it works

```
PDF -> text per page -> chunks (400 chars, 80 overlap) -> embeddings -> ChromaDB
Question -> top-5 chunks -> distance gate (0.71) -> LLM with a strict prompt -> answer + sources
```

- The distance gate refuses questions far from any document without calling the LLM.
- The prompt tells the model to answer only with facts explicitly stated in the context.
- `POST /ask` is protected by an API key read from an environment variable.

## Results (internal evaluation on fictional documents)

| What | Result |
|---|---|
| Retrieval, 26 questions | hit@1 80.8%, hit@3 92.3% |
| Same set before fixing a chunking bug the evaluation exposed | hit@1 53.8%, hit@3 61.5% |
| Answers, 26 in-scope questions (regex-checked) | 26/26 |
| Out-of-scope questions refused | 4/4 |
| Near-miss and held-out questions (12) | 10 refused cleanly, 2 answered "not mentioned" |
| API tests (fake backend) | 6, run on every push with GitHub Actions |
| Docker image built from scratch and checked end to end | 5/5 checks passed |

## Known limitations

- Small fictional dataset (4 documents). The evaluation questions were written by the
  author, and the 0.71 distance threshold was set from only 4 out-of-scope questions.
- The 3B model sometimes answers "No, ... not mentioned" for topics missing from the
  documents. The content is honest, but the leading "No" can be read as a prohibition.
- English only. Sources show the 2 closest chunks, not necessarily the ones the model used.

## Run locally

Requirements: Python 3.12, [Ollama](https://ollama.com), and `ollama pull llama3.2:3b`.

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/ingest.py
$env:DOC_ASSISTANT_API_KEY = "choose-a-long-random-key"
uvicorn api:app --app-dir src
```

Open http://127.0.0.1:8000/docs and call `POST /ask` with the header `x-api-key`.

## Run with Docker

Ollama must be running on the host (the command below assumes Docker Desktop).
The build downloads the embedding model with retries and builds the vector database.

```
docker build -t doc-assistant .
docker run --rm -p 8000:8000 -e DOC_ASSISTANT_API_KEY=your-key -e OLLAMA_HOST=http://host.docker.internal:11434 doc-assistant
```

Then check the running service (same key):

```
python src/check_api.py
```

## API

- `GET /health`: service status.
- `POST /ask` with header `x-api-key` and body `{"question": "..."}` returns the answer,
  up to 2 sources, the top distance, whether the question was refused, and the latency.

## Evaluation and tests

- `src/eval_retrieval.py`: hit@1 and hit@3 on 26 questions, plus distances of out-of-scope questions.
- `src/eval_answers.py`: answer check on the same questions.
- `src/eval_near_miss.py`: questions close to the documents' topics whose answers are not in them.
- `src/check_api.py`: end-to-end check of a running server.
- `pytest`: API tests