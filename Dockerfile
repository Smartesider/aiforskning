FROM python:3.11-slim

# Non-root user for Flask application
RUN groupadd -r flaskapp && useradd -r -g flaskapp flaskapp

WORKDIR /app

# Install dependencies for MariaDB
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN chown -R flaskapp:flaskapp /app

USER flaskapp

EXPOSE 8010

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run_app:app
ENV FLASK_ENV=production

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8010/health/ || exit 1

CMD ["gunicorn", "run_app:app", "--bind", "0.0.0.0:8010", "--workers", "3"]
