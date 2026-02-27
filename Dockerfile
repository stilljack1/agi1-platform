FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install requests uvicorn fastapi
# This command tells Render to start the core loop and listen on port 10000
CMD ["uvicorn", "core.ralph_loop:app", "--host", "0.0.0.0", "--port", "10000"]
