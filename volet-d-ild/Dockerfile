FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY pipeline/ ./pipeline/
# static/ studio UI inclus dans api/static/
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENV DONNEES_PATH=/data

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
