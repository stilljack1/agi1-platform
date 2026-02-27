FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install requests uvicorn fastapi
# Use the PORT environment variable provided by Render
CMD uvicorn core.ralph_loop:app --host 0.0.0.0 --port ${PORT:-10000}
