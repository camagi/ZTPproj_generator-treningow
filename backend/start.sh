#!/bin/sh
set -e

python migrate.py
python seed_data.py --skip-if-populated
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
