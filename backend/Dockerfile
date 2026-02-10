FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Create a non-root user
RUN useradd -m appuser

# Run unprivileged
USER appuser

# Expose port (added for web server)
EXPOSE 8000


# Run uvicorn server
CMD ["uvicorn", "github_pull_request_status_cli.api:app", "--host", "0.0.0.0", "--port", "8000"]
