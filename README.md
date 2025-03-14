# Task Management Application
Full name: Kiều Trương Hàm Hương
Student ID: 22719241
A Flask-based task management application that allows users to create, manage, and track tasks.

## Prerequisites

- Python 3.x installed on your system
- Git (optional, for cloning the repository)

## Getting Started

1. Clone the repository (if you haven't already):
   ```bash
   git clone https://github.com/HamHuong/ptud-gk-de2.git
   cd GK
   ```

2. Running the Application

   ### On Windows:
   Simply double-click the `run.bat` file or run it from the command prompt:
   ```cmd
   run.bat
   ```

   ### On Unix/Linux/MacOS:
   Execute the shell script:
   ```bash
   ./run.sh
   ```

   The scripts will automatically:
   - Check if Python is installed
   - Create a virtual environment if it doesn't exist
   - Install all required dependencies
   - Initialize the database
   - Start the Flask application

3. Access the Application
   - Open your web browser and navigate to: http://localhost:5000
   - Default admin credentials:
     - Username: admin
     - Password: admin123

## Manual Setup (if scripts don't work)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```cmd
     venv\Scripts\activate
     ```
   - Unix/Linux/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the application:
   ```bash
   python app.py
   ```

## Features

- Task creation and management
- Task status tracking
- Admin dashboard
- User authentication
- Task completion time tracking

