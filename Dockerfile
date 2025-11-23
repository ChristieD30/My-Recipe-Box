# Dockerfile - Optimized for production
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc sqlite3 curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories
RUN mkdir -p app/static/uploads/recipes && chmod 755 app/static/uploads/recipes

# Create user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Optimized startup - skip heavy database seeding in production
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--preload", \
     "--timeout", "30", \
     "--access-logfile", "-", \
     "run:app"]