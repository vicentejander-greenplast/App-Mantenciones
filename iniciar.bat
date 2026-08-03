@echo off
chcp 65001 > nul
echo.
echo  ============================================================
echo    GREENPLAST — App de Mantenciones
echo    Abre tu navegador en: http://localhost:5001
echo  ============================================================
echo.
start "" http://localhost:5001
python app.py
pause
