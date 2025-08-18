@echo off
title FoodOps Pro - Launcher
echo.
echo 🚀 FOODOPS PRO - LAUNCHER
echo =========================
echo.
echo Choisissez votre launcher :
echo.
echo 1. 💻 Launcher Console (Recommandé)
echo    → Ouvre les jeux dans de nouvelles consoles
echo.
echo 2. 🌐 Launcher Web
echo    → Interface web avec instructions
echo.
echo 3. 🎮 Lancer directement FoodOps Pro
echo.

set /p choice="👉 Votre choix (1-3) : "

if "%choice%"=="1" (
    echo.
    echo 💻 Lancement du launcher console...
    python launcher_console.py
) else if "%choice%"=="2" (
    echo.
    echo 🌐 Ouverture du launcher web...
    start "" "launcher.html"
    echo ✅ Launcher web ouvert dans votre navigateur !
) else if "%choice%"=="3" (
    echo.
    echo 🎮 Lancement direct de FoodOps Pro...
    python start_pro.py
) else (
    echo.
    echo ❌ Choix invalide. Lancement du launcher console par défaut...
    python launcher_console.py
)

echo.
pause
