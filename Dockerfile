FROM python:3.9-slim
WORKDIR /app
COPY . .
# Set the PYTHONPATH so it can see agent_gateway
ENV PYTHONPATH=/app:/app/core
# Added aiohttp to the install list
RUN pip install requests uvicorn fastapi aiohttp
CMD uvicorn core.ralph_loop:app --host 0.0.0.0 --port ${PORT:-10000}
