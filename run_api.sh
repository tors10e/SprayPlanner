#!/bin/bash

# Navigate to the project root (where the script is located)
cd "$(dirname "$0")"

# Activate the virtual environment
if [ -f "sprayplan_env/bin/activate" ]; then
    source SprayPlanner/sprayplan_env/bin/activate
else
    echo "Error: Virtual environment not found at sprayplan_env"
    exit 1
fi

# Set PYTHONPATH to include the api directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/SprayPlanner/api

echo "Starting Spray Chemical Database API on http://localhost:5001..."
# Start the Flask API
python3 api/api.py
