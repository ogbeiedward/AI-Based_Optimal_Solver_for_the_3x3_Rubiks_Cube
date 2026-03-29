FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
# Using CPU-only version of torch to save space and memory
COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt

# Copy project files
COPY . .

# Set environment variables for the server
ENV HOST=0.0.0.0
ENV PORT=7860
EXPOSE 7860

# Command to run the visualizer server
CMD ["python", "visualization/server.py", "--port", "7860"]
