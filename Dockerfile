FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install requests uvicorn fastapi
# This tells uvicorn to use the PORT Render provides, or default to 10000
CMD uvicorn core.ralph_loop:app --host 0.0.0.0 --port ${PORT:-10000}
