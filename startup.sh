#!/bin/bash

# Install system dependencies
apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    libsm6 \
    libxext6

# Activate virtual environment
source /antenv/bin/activate

# Run Gunicorn
exec gunicorn --bind=0.0.0.0:8000 --timeout 1200 --workers 1 run:app