@echo off
REM Metashape Configuration Tool - GENERIC VERSION
REM =============================================
REM Batch file to start the Metashape configuration tool
REM Generic version with configurable paths
REM
REM USAGE:
REM 1. Edit the paths below to match your setup
REM 2. Double-click this file to run the configuration tool
REM 3. Alternatively, run from command line: start_config_tool_generic.bat

REM =============================================================================
REM CONFIGURATION SECTION - EDIT THESE PATHS FOR YOUR ENVIRONMENT
REM =============================================================================

REM Set the path to your Python executable
REM Examples:
REM   Standard Python: C:\Python39\python.exe
REM   Anaconda/Miniconda: C:\Users\YourUsername\anaconda3\python.exe
REM   Virtual Environment: C:\Your\VirtualEnv\Scripts\python.exe
set PYTHON_PATH=python

REM Set the path to the folder containing this batch file and the config tool
REM This should be the path to your generic scripts folder
REM Example: C:\Your\Project\Scripts\Generic
set SCRIPT_FOLDER=%~dp0

REM Set the path to the config tool script
set CONFIG_TOOL_SCRIPT=%SCRIPT_FOLDER%config_tool_generic.py

REM Optional: Set default script folder if different from this folder
REM Leave empty to use current folder as default
set DEFAULT_SCRIPT_FOLDER=%SCRIPT_FOLDER%

REM =============================================================================
REM EXECUTION SECTION - DO NOT EDIT BELOW THIS LINE
REM =============================================================================

echo Starting Metashape Configuration Tool - Generic Version
echo ========================================================
echo.
echo Python Path: %PYTHON_PATH%
echo Script Folder: %SCRIPT_FOLDER%
echo Config Tool: %CONFIG_TOOL_SCRIPT%
echo.

REM Check if Python is available
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found at: %PYTHON_PATH%
    echo.
    echo Please edit this batch file and set the correct PYTHON_PATH
    echo Examples:
    echo   Standard Python: set PYTHON_PATH=C:\Python39\python.exe
    echo   Anaconda: set PYTHON_PATH=C:\Users\YourUsername\anaconda3\python.exe
    echo   Virtual Env: set PYTHON_PATH=C:\Your\VirtualEnv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

REM Check if config tool script exists
if not exist "%CONFIG_TOOL_SCRIPT%" (
    echo ERROR: Config tool script not found at: %CONFIG_TOOL_SCRIPT%
    echo.
    echo Please make sure the config_tool_generic.py file is in the same folder as this batch file
    echo Current folder: %SCRIPT_FOLDER%
    echo.
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%SCRIPT_FOLDER%"

REM Run the configuration tool
echo Launching configuration tool...
"%PYTHON_PATH%" "%CONFIG_TOOL_SCRIPT%"

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo ERROR: Configuration tool failed to start
    echo This might be due to missing Python packages
    echo.
    echo Required packages: tkinter (usually included with Python)
    echo.
    echo Try running from command line to see detailed error messages:
    echo "%PYTHON_PATH%" "%CONFIG_TOOL_SCRIPT%"
    echo.
    pause
    exit /b 1
)

echo.
echo Configuration tool closed successfully
pause
