#!/bin/bash

# Navigate to the project root (where the script is located)
cd "$(dirname "$0")"

# Activate the virtual environment
if [ -f "sprayplan_env/bin/activate" ]; then
    source sprayplan_env/bin/activate
elif [ -f "../sprayplan_env/bin/activate" ]; then
    source ../sprayplan_env/bin/activate
else
    echo "Error: Virtual environment not found at sprayplan_env"
    exit 1
fi

# Set PYTHONPATH to include the api directory
# This allows 'import core', 'import services', etc. to work from within the api directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/api

echo "Starting Spray Planner CLI..."
# Start the CLI app
# We run it from the 'api' directory so relative paths in config.py work as expected
cd api
python3 app.py
