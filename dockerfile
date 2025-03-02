FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose API port
EXPOSE 8001

# Command to run the API
CMD ["uvicorn", "unified_ai_agent:app", "--host", "0.0.0.0", "--port", "8001"]
