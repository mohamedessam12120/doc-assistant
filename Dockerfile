FROM python:3.12-slim

RUN useradd --create-home app
WORKDIR /app
RUN chown app:app /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER app
COPY --chown=app:app docs/ docs/
COPY --chown=app:app src/ src/

# Build the vector database at image build time (this also caches the embedding model)
RUN python src/ingest.py

EXPOSE 8000
CMD ["uvicorn", "api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]