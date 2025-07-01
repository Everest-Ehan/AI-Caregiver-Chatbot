#!/bin/bash

# Activate virtual environment
source /opt/venv/bin/activate

# Verify Python version and location
echo "Using Python: $(which python)"
echo "Python version: $(python --version)"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000 