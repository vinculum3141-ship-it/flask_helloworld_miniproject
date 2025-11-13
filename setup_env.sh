#!/bin/bash
# Source this file before working on the project
# Usage: source setup_env.sh

# Activate virtual environment
source /home/ruby/Projects/courses/halloworld_testengineer/.venv/bin/activate

# Set PYTHONPATH to include the app directory
export PYTHONPATH="${PYTHONPATH}:/home/ruby/Projects/courses/halloworld_testengineer/flask-k8s/app"

echo "Environment setup complete!"
echo "You can now run: pytest app/tests/ -v"