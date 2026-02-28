FROM python:3.9-slim
WORKDIR /app
COPY . .
# Set the PYTHONPATH to include the current directory and core
ENV PYTHONPATH=/app:/app/core
RUN pip install requests uvicorn fastapi
# Start from the app root and point to core.ralph_loop
CMD uvicorn core.ralph_loop:app --host 0.0.0.0 --port ${PORT:-10000}
