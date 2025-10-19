@echo off
title GameDev AI Assistant
color 0A

echo.
echo ========================================
echo   GameDev AI Assistant v1.0.0
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Install from: python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama not running
    echo AI features need Ollama
    echo.
    pause
)

echo Starting application...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application error
    pause
)