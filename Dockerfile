FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy requirements (if you have them, otherwise we install basics)
# RUN pip install --no-cache-dir -r requirements.txt
# For now, we install the core requirements manually
RUN pip install requests

# Copy the entire project into the container
COPY . .

# Initialize the database
RUN python3 -c "import sqlite3; conn = sqlite3.connect('agi1_persistence.db'); c = conn.cursor(); c.execute('CREATE TABLE IF NOT EXISTS agent_registry (role TEXT)'); conn.close()"

# The Command to Run 24/7 (Supervisor)
CMD ["python3", "services/supervisor/supervisor.py"]
