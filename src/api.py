import logging
import os
import time

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from ask import ask_detailed

# The key comes from an environment variable, never from the code or the repo
API_KEY = os.environ.get("DOC_ASSISTANT_API_KEY", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("api")

app = FastAPI(title="Company Policy Assistant")


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=500)


def check_key(x_api_key: str = Header(default="")):
    # Fail closed: if no key is configured on the server, nobody gets in
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", dependencies=[Depends(check_key)])
def ask_endpoint(body: Question):
    start = time.perf_counter()
    result = ask_detailed(body.question.strip())
    ms = round((time.perf_counter() - start) * 1000)
    # Log metadata only, not the question text (employee questions can be sensitive)
    log.info("refused=%s top_distance=%s question_chars=%d latency_ms=%d",
             result["refused"], result["top_distance"], len(body.question), ms)
    return {**result, "latency_ms": ms}