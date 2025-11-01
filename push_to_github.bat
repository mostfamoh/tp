@echo off
echo ========================================
echo   PUSH TO GITHUB - TP SSAD USTHB
echo ========================================
echo.

REM Vérifier si git est installé
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Git n'est pas installé ou pas dans le PATH!
    echo Téléchargez Git depuis: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/5] Initialisation du dépôt Git...
git init
echo.

echo [2/5] Ajout du remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/mostfamoh/tp.git
echo.

echo [3/5] Ajout de tous les fichiers...
git add .
echo.

echo [4/5] Création du commit...
git commit -m "Initial commit - Crypto Lab TP SSAD USTHB"
echo.

echo [5/5] Push vers GitHub...
echo.
echo ATTENTION: Vous allez être invité à entrer vos identifiants GitHub
echo Si vous avez l'authentification à 2 facteurs, utilisez un Personal Access Token
echo.
pause

REM Push vers la branche main
git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCÈS! Projet poussé sur GitHub
    echo   URL: https://github.com/mostfamoh/tp
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   ERREUR lors du push!
    echo ========================================
    echo.
    echo Solutions possibles:
    echo 1. Vérifiez vos identifiants GitHub
    echo 2. Si vous avez 2FA activé, créez un Personal Access Token:
    echo    - https://github.com/settings/tokens
    echo    - Utilisez le token comme mot de passe
    echo 3. Vérifiez que le dépôt existe: https://github.com/mostfamoh/tp
    echo.
)

pause
