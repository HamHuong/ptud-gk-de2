#!/bin/bash

echo "Starting Task Management Application Setup..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed! Please install Python 3.x"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python init_db.py

# Run the application
echo "Starting Flask application..."
echo "Access the application at http://localhost:5000"
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin123"
python app.py 