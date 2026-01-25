FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for pdf2image
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (from backend/ relative to build context which is repo root)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Create directories for data and locks
RUN mkdir -p /app/data /app/locks

# Expose port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
