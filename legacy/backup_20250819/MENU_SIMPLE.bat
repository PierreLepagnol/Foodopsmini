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
echo      Interface enrichie avec fonds de commerce
echo.
echo   2. Mode Administrateur (Professeurs)
echo      Configuration de partie et presets
echo.
echo   3. Demonstration Rapide
echo      Apercu des fonctionnalites
echo.
echo   4. Version Classique
echo      Jeu simple et rapide
echo.
echo   0. Quitter
echo.

set /p choice="Votre choix (0-4) : "

if "%choice%"=="0" goto EXIT
if "%choice%"=="1" goto JOUER_PRO
if "%choice%"=="2" goto MODE_ADMIN
if "%choice%"=="3" goto DEMO_RAPIDE
if "%choice%"=="4" goto VERSION_CLASSIQUE

echo.
echo Choix invalide. Utilisez 0-4.
pause
goto MENU

:JOUER_PRO
cls
echo.
echo LANCEMENT FOODOPS PRO - VERSION COMPLETE
echo ========================================
echo.
echo Ouverture dans une nouvelle console...
start "FoodOps Pro - Version Complete" cmd /k "python start_pro.py"
echo.
echo FoodOps Pro lance dans une nouvelle fenetre !
echo Vous pouvez fermer cette fenetre.
echo.
pause
goto MENU

:MODE_ADMIN
cls
echo.
echo LANCEMENT MODE ADMINISTRATEUR
echo =============================
echo.
echo Ouverture dans une nouvelle console...
start "FoodOps Pro - Mode Admin" cmd /k "python start_admin.py"
echo.
echo Mode Admin lance dans une nouvelle fenetre !
echo Vous pouvez fermer cette fenetre.
echo.
pause
goto MENU

:DEMO_RAPIDE
cls
echo.
echo LANCEMENT DEMONSTRATION
echo =======================
echo.
echo Ouverture dans une nouvelle console...
start "FoodOps Pro - Demo" cmd /k "python demo_pro.py"
echo.
echo Demonstration lancee dans une nouvelle fenetre !
echo Vous pouvez fermer cette fenetre.
echo.
pause
goto MENU

:VERSION_CLASSIQUE
cls
echo.
echo LANCEMENT VERSION CLASSIQUE
echo ===========================
echo.
echo Ouverture dans une nouvelle console...
start "FoodOps Pro - Classique" cmd /k "python -m src.foodops_pro.cli"
echo.
echo Version Classique lancee dans une nouvelle fenetre !
echo Vous pouvez fermer cette fenetre.
echo.
pause
goto MENU

:EXIT
cls
echo.
echo MERCI D'AVOIR UTILISE FOODOPS PRO !
echo ===================================
echo.
echo Objectif atteint : Apprendre la gestion en s'amusant !
echo Ideal pour : Cours de gestion, entrepreneuriat, comptabilite
echo.
pause
exit
