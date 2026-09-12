FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Agent 4 performs CPU-only embedding inference. Install a CPU wheel first so
# sentence-transformers does not pull unnecessary CUDA runtime libraries.
RUN pip install --no-cache-dir "torch==2.4.1" --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Preload the embedding model at image build time to reduce Space cold starts.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0"]
