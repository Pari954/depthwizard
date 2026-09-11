# DepthWizard Dockerfile (SIH26175)
FROM python:3.11-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Generate sample scenes if needed
RUN python backend/generate_samples.py

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
