FROM python:3.9-slim
WORKDIR /app
COPY . .
# Explicitly add the core directory to PYTHONPATH
ENV PYTHONPATH=/app/core
RUN pip install requests uvicorn fastapi
CMD uvicorn core.ralph_loop:app --host 0.0.0.0 --port ${PORT:-10000}
