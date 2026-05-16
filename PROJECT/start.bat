@echo off
echo =========================================
echo Starting PRODUCT THINKER
echo =========================================
echo.
echo Make sure Ollama is running in the background!
echo.
echo Starting FastAPI Server...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
