#!/bin/sh
set -e
if [ "$AUTO_INGEST_ON_START" = "true" ]; then
  echo "=== Ingestion automatique au démarrage ==="
  python -m pipeline.ingest
else
  echo "=== API seule — lancez le pipeline depuis http://localhost:8000/studio ==="
fi
exec uvicorn api.main:app --host 0.0.0.0 --port 8000
