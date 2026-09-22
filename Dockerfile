FROM python:3.12-slim

# System dependencies: libmagic1 for python-magic
RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy models at build time
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application
COPY . .

# Railway sets $PORT at runtime; default to 8080 for local testing
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]