#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Start Gunicorn (adjust timeout if needed)
gunicorn --bind=0.0.0.0:80 --timeout 600 run:app