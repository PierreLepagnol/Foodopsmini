@echo off
title FoodOps Pro - Menu Principal
color 0A

:MENU
cls
echo.
echo ================================================
echo            FOODOPS PRO - MENU PRINCIPAL
echo ================================================
echo.
echo CHOISISSEZ VOTRE MODE DE JEU :
echo.
echo   1. Jouer Pro (Version complete)
echo      - Fonds de commerce, decisions avancees
echo.
echo   2. Mode Administrateur (Professeurs)
echo      - Configuration de partie, presets
echo.
echo   3. Demonstration Rapide
echo      - Apercu des fonctionnalites
echo.
echo   4. Version Classique
echo      - Jeu simple et rapide
echo.
echo   5. Demos Techniques
echo      - Voir le code en action
echo.
echo   0. Quitter
echo.

set /p choice="Votre choix (0-5) : "

if "%choice%"=="0" goto EXIT
if "%choice%"=="1" goto JOUER_PRO
if "%choice%"=="2" goto MODE_ADMIN
if "%choice%"=="3" goto DEMO_RAPIDE
if "%choice%"=="4" goto VERSION_CLASSIQUE
if "%choice%"=="5" goto DEMOS_TECH

echo.
echo Choix invalide. Utilisez 0-5.
pause
goto MENU

:JOUER_PRO
cls
echo.
echo LANCEMENT FOODOPS PRO - VERSION COMPLETE
echo ========================================
echo Interface enrichie avec fonds de commerce
echo Menu de decisions avance et rapports financiers
echo ========================================
echo.
echo Ouverture dans une nouvelle console...
start "FoodOps Pro - Version Complete" cmd /k "python start_pro.py"
echo FoodOps Pro lance dans une nouvelle fenetre !
echo.
pause
goto MENU

:MODE_ADMIN
cls
echo.
echo 👨‍🏫 LANCEMENT MODE ADMINISTRATEUR
echo =================================
echo Interface de configuration pour professeurs
echo Configurez tous les paramètres de la partie
echo =================================
echo.
echo ⏳ Ouverture dans une nouvelle console...
start "FoodOps Pro - Mode Admin" cmd /k "python start_admin.py"
echo ✅ Mode Admin lancé dans une nouvelle fenêtre !
echo.
pause
goto MENU

:DEMO_RAPIDE
cls
echo.
echo 🧪 LANCEMENT DÉMONSTRATION
echo ==========================
echo Découvrez toutes les fonctionnalités
echo Interface, commerce, KPIs, rapports
echo ==========================
echo.
echo ⏳ Ouverture dans une nouvelle console...
start "FoodOps Pro - Démo" cmd /k "python demo_pro.py"
echo ✅ Démonstration lancée dans une nouvelle fenêtre !
echo.
pause
goto MENU

:VERSION_CLASSIQUE
cls
echo.
echo 🎮 LANCEMENT VERSION CLASSIQUE
echo ==============================
echo Jeu simple et rapide
echo Interface console basique
echo ==============================
echo.
echo ⏳ Ouverture dans une nouvelle console...
start "FoodOps Pro - Classique" cmd /k "python -m src.foodops_pro.cli"
echo ✅ Version Classique lancée dans une nouvelle fenêtre !
echo.
pause
goto MENU

:DEMOS_TECH
cls
echo.
echo 📊 DÉMOS TECHNIQUES
echo ==================
echo.
echo   a. 🔧 Démo Classique (chargement, coûts, marché)
echo   b. ✨ Démo Pro (UI, commerce, KPIs, P&L)
echo   c. 🔙 Retour au menu principal
echo.

set /p demo_choice="👉 Votre choix (a/b/c) : "

if "%demo_choice%"=="c" goto MENU
if "%demo_choice%"=="a" (
    echo.
    echo ⏳ Lancement Démo Classique...
    start "FoodOps Pro - Démo Classique" cmd /k "python demo.py"
    echo ✅ Démo Classique lancée !
    pause
    goto MENU
)
if "%demo_choice%"=="b" (
    echo.
    echo ⏳ Lancement Démo Pro...
    start "FoodOps Pro - Démo Pro" cmd /k "python demo_pro.py"
    echo ✅ Démo Pro lancée !
    pause
    goto MENU
)

echo.
echo ❌ Choix invalide. Utilisez a, b ou c.
pause
goto DEMOS_TECH

:EXIT
cls
echo.
echo 👋 MERCI D'AVOIR UTILISÉ FOODOPS PRO !
echo =====================================
echo.
echo 🎯 Objectif atteint : Apprendre la gestion en s'amusant !
echo 📚 Idéal pour : Cours de gestion, entrepreneuriat, comptabilité
echo.
echo 💡 N'hésitez pas à relancer le menu pour jouer à nouveau !
echo.
pause
exit
