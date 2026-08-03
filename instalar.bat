@echo off
chcp 65001 > nul
echo.
echo  ============================================================
echo    GREENPLAST — Instalador de App de Mantenciones
echo  ============================================================
echo.
echo  Instalando dependencias Python...
echo.

pip install -r requirements.txt

echo.
echo  ============================================================
echo    Instalacion completada.
echo    Ejecuta "iniciar.bat" para arrancar la app.
echo  ============================================================
echo.
pause
