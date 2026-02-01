FROM python:3.9-slim

WORKDIR /app

# Copy Config
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy App Code
COPY . .

# Set Path
ENV PYTHONPATH=/app

# Expose Port
EXPOSE 8000

# Start Command
CMD ["uvicorn", "control_plane:app", "--host", "0.0.0.0", "--port", "8000"]
