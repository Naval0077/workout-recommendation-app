#!/bin/bash

# Exit immediately on error
set -e

export PIP_NO_CACHE_DIR=true
export TMPDIR=/tmp
mkdir -p $TMPDIR

# Install dependencies in stages (avoids timeouts)
echo "Installing core dependencies..."
pip install --no-cache-dir -r requirements-core.txt

echo "Installing ML dependencies..."
pip install --no-cache-dir -r requirements-ml.txt

# Pre-load ML models (reduces first-request latency)
echo "Pre-loading ML models..."
python -c "
from sentence_transformers import SentenceTransformer;
SentenceTransformer('all-MiniLM-L6-v2', device='cpu');
import mediapipe as mp;
mp.solutions.holistic.Holistic(min_detection_confidence=0.5);
"

# Start Gunicorn with optimized settings
echo "Starting Gunicorn..."
exec gunicorn --bind=0.0.0.0:80 \
    --timeout 1200 \
    --workers 2 \
    --threads 4 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    run:app