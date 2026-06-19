FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies (build-essential is required for ChromaDB's dependencies like hnswlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for caching
COPY backend/requirements.txt ./backend/

# Install python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code and data folder
COPY backend/ ./backend/
COPY data/ ./data/

# Expose Hugging Face Space port
EXPOSE 7860

# Command to run the FastAPI app using uvicorn, importing backend.main:app from the root
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
