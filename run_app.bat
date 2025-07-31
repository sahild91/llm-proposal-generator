@echo off
REM LLM Proposal Generator Startup Script for Windows

echo Starting LLM Proposal Generator...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Please make sure you're running this from the application directory
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import requests, yaml" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if configuration exists
if not exist "config\llm_config.yaml" (
    if exist "config\llm_config.yaml.example" (
        echo Creating default configuration...
        copy "config\llm_config.yaml.example" "config\llm_config.yaml"
        echo.
        echo IMPORTANT: Please edit config\llm_config.yaml with your API keys
        echo before using the application.
        echo.
    )
)

REM Create directories if they don't exist
if not exist "Projects" mkdir Projects
if not exist "config" mkdir config

REM Start the application
echo Starting application...
echo.
python main.py

REM Handle exit
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    echo Check the error messages above for details.
) else (
    echo.
    echo Application closed normally.
)

echo.
echo Press any key to exit...
pause >nul