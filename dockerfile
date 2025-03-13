# Use a minimal base image for security
FROM python:3.10-slim

# Set a non-root user for security
RUN useradd -m appuser
USER appuser

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements first (to optimize caching)
COPY --chown=appuser:appuser requirements.txt .

# Install dependencies in user space (avoids permission issues)
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Expose API port
EXPOSE 8001

# Healthcheck (optional but recommended)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Command to run the API
CMD ["uvicorn", "unified_ai_agent:app", "--host", "0.0.0.0", "--port", "8001"]
