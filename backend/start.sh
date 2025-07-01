#!/bin/bash

# Activate virtual environment
source /opt/venv/bin/activate

# Verify Python version and location
echo "Using Python: $(which python)"
echo "Python version: $(python --version)"

# Check if required environment variables are set
echo "Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY is not set!"
    exit 1
else
    echo "✓ OPENAI_API_KEY is set"
fi

echo "HOST: ${HOST:-0.0.0.0}"
echo "PORT: ${PORT:-8000}"
echo "DEBUG: ${DEBUG:-False}"

# Test Python imports
echo "Testing Python imports..."
python -c "
import sys
try:
    from fastapi import FastAPI
    print('✓ FastAPI imported successfully')
except ImportError as e:
    print(f'✗ Failed to import FastAPI: {e}')
    sys.exit(1)

try:
    from agents.caregiver_agent import chat_graph
    print('✓ caregiver_agent imported successfully')
except ImportError as e:
    print(f'✗ Failed to import caregiver_agent: {e}')
    sys.exit(1)

try:
    from config import Config
    Config.validate()
    print('✓ Config validated successfully')
except Exception as e:
    print(f'✗ Config validation failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "ERROR: Python import test failed!"
    exit 1
fi

echo "Starting the application..."
# Start the application with more verbose logging
exec uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug 