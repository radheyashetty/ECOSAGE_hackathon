@echo off
setlocal enabledelayedexpansion
title EcoSage - AI Environmental Scientist

:: Ensure current directory is in PYTHONPATH for Python imports
set PYTHONPATH=%CD%;%PYTHONPATH%

:: Activate virtual environment if present
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

:: Verify python is accessible
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.11+ or ensure it is added to your environment variables.
    pause
    exit /b 1
)

:MENU
cls
echo =====================================================================
echo    EcoSage: AI Environmental Scientist for Biodiversity
echo =====================================================================
echo    Evidence-Grounded RAG ^| Causal Knowledge Graph ^| Zero-Cost (Rs 0)
echo =====================================================================
echo.
echo   [1] Launch Streamlit UI (Frontend Dashboard - Recommended)
echo   [2] Launch Full Stack (FastAPI Backend + Streamlit UI)
echo   [3] Launch FastAPI Backend Server Only (Port 8000)
echo   [4] Ingest Knowledge Base into ChromaDB (60 Chunks)
echo   [5] Run Full Test Suite (pytest - 140 Tests)
echo   [6] Run Code Quality Check (Ruff Linter)
echo   [0] Exit
echo.
echo =====================================================================
set /p choice="Select an option [1-6, default=1]: "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto STREAMLIT
if "%choice%"=="2" goto FULLSTACK
if "%choice%"=="3" goto BACKEND
if "%choice%"=="4" goto INGEST
if "%choice%"=="5" goto TESTS
if "%choice%"=="6" goto LINT
if "%choice%"=="0" goto EXIT

echo [!] Invalid selection, please enter a number from 0 to 6.
timeout /t 2 >nul
goto MENU

:STREAMLIT
cls
echo [INFO] Starting EcoSage Streamlit Dashboard...
echo [INFO] Standalone in-process execution is enabled.
echo [INFO] Press Ctrl+C in this window to stop the server.
echo.
streamlit run ui/app.py
pause
goto MENU

:FULLSTACK
cls
echo [INFO] Starting FastAPI Backend on port 8000 in a new window...
start "EcoSage FastAPI Backend" cmd /k "title EcoSage API Server && uvicorn ecosage.api:app --reload --port 8000"
echo [INFO] Waiting 2 seconds for API to initialize...
timeout /t 2 /nobreak >nul
echo [INFO] Starting Streamlit UI...
streamlit run ui/app.py
pause
goto MENU

:BACKEND
cls
echo [INFO] Starting FastAPI Backend on http://localhost:8000 ...
echo [INFO] Interactive docs at http://localhost:8000/docs
echo.
uvicorn ecosage.api:app --reload --port 8000
pause
goto MENU

:INGEST
cls
echo [INFO] Ingesting knowledge base into ChromaDB...
python -m ecosage.ingest
echo.
echo [DONE] Ingestion complete.
pause
goto MENU

:TESTS
cls
echo [INFO] Running complete test suite (140 tests)...
python -m pytest -v
echo.
pause
goto MENU

:LINT
cls
echo [INFO] Checking code quality with Ruff...
python -m ruff check ecosage/ tests/ ui/
echo.
pause
goto MENU

:EXIT
cls
echo Thank you for using EcoSage!
timeout /t 1 >nul
exit /b 0


