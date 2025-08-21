@echo off
title FoodOps Pro - Simulateur de Restaurant
color 0A

echo.
echo ========================================
echo    🍽️ FOODOPS PRO - LANCEMENT 🍽️
echo ========================================
echo.
echo 🎯 Simulateur de gestion de restaurant
echo 📚 Version de démonstration
echo.

cd /d "%~dp0"

echo 🔍 Vérification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trouvé !
    echo 💡 Installez Python depuis python.org
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.
echo 🚀 Lancement du jeu...
echo.

python foodops_demo_direct.py

echo.
echo 👋 Merci d'avoir joué !
pause
