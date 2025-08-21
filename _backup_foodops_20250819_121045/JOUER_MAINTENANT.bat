@echo off
echo 🎮 LANCEMENT FOODOPS PRO
echo ========================
echo.

REM Essayer Python système d'abord
where python >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python système trouvé
    python jouer_pro_simple.py
    goto :end
)

REM Essayer python.exe
where python.exe >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python.exe trouvé
    python.exe jouer_pro_simple.py
    goto :end
)

REM Essayer py
where py >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Py launcher trouvé
    py jouer_pro_simple.py
    goto :end
)

echo ❌ Python non trouvé
echo Installez Python depuis https://python.org
pause

:end
echo.
echo 👋 Merci d'avoir joué !
pause
