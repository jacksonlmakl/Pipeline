#!/bin/bash

# Check if the virtual environment "env" exists
if [ ! -d "env" ]; then
    echo "Creating virtual environment 'env'..."
    python3 -m venv env
    
    # Activate the virtual environment
    source env/bin/activate

    # Install dependencies from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "No requirements.txt found, skipping dependency installation."
    fi
else
    echo "Virtual environment 'env' already exists."
    
    # Activate the virtual environment
    source env/bin/activate
fi

# Check if a filename argument was passed
if [ -z "$1" ]; then
    echo "Error: No file name provided."
    echo "Usage: ./run_pipeline.sh <file_name>"
    exit 1
fi

# Get the filename from the argument
file_name=$1

# Generate the Python code dynamically
python_code="
from core import Pipeline

file_name = '$file_name'
p = Pipeline(file_name)
print(f'Pipeline {file_name} Started.....')
p.start()
"

# Save the Python code to a temporary file
echo "$python_code" > run_pipeline.py

# Run the Python script
python run_pipeline.py

# Optionally, clean up by removing the temporary Python file
rm run_pipeline.py

# Deactivate the virtual environment
deactivate

