# Script PowerShell pour pousser le projet vers GitHub
# TP SSAD USTHB - Crypto Lab

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PUSH TO GITHUB - TP SSAD USTHB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si git est installé
try {
    $gitVersion = git --version
    Write-Host "✓ Git détecté: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERREUR: Git n'est pas installé!" -ForegroundColor Red
    Write-Host "Téléchargez Git depuis: https://git-scm.com/download/win" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "[1/5] Initialisation du dépôt Git..." -ForegroundColor Yellow
git init
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dépôt initialisé" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/5] Configuration du remote origin..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/mostfamoh/tp.git
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Remote ajouté: https://github.com/mostfamoh/tp.git" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/5] Ajout de tous les fichiers..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -eq 0) {
    $fileCount = (git diff --cached --name-only).Count
    Write-Host "✓ $fileCount fichier(s) ajouté(s)" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/5] Création du commit..." -ForegroundColor Yellow
git commit -m "Initial commit - Crypto Lab TP SSAD USTHB - Complete project with frontend and backend"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Commit créé" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/5] Push vers GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATTENTION" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Vous allez être invité à entrer vos identifiants GitHub" -ForegroundColor White
Write-Host ""
Write-Host "Si vous avez l'authentification à 2 facteurs (2FA):" -ForegroundColor Yellow
Write-Host "1. Allez sur: https://github.com/settings/tokens" -ForegroundColor White
Write-Host "2. Créez un 'Personal Access Token' (Classic)" -ForegroundColor White
Write-Host "3. Sélectionnez le scope 'repo'" -ForegroundColor White
Write-Host "4. Utilisez le token comme MOT DE PASSE" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur une touche pour continuer..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ SUCCÈS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Projet poussé avec succès sur GitHub!" -ForegroundColor White
    Write-Host "URL: https://github.com/mostfamoh/tp" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Vous pouvez maintenant:" -ForegroundColor Yellow
    Write-Host "  1. Voir votre projet sur: https://github.com/mostfamoh/tp" -ForegroundColor White
    Write-Host "  2. Cloner le projet: git clone https://github.com/mostfamoh/tp.git" -ForegroundColor White
    Write-Host "  3. Partager le lien avec votre professeur" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ✗ ERREUR lors du push!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions possibles:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Vérifiez que le dépôt existe:" -ForegroundColor White
    Write-Host "   → https://github.com/mostfamoh/tp" -ForegroundColor Cyan
    Write-Host "   → Si le dépôt n'existe pas, créez-le d'abord sur GitHub" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Si vous avez 2FA activé:" -ForegroundColor White
    Write-Host "   → Créez un Personal Access Token" -ForegroundColor Gray
    Write-Host "   → https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "   → Utilisez le token comme mot de passe" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Vérifiez vos identifiants:" -ForegroundColor White
    Write-Host "   → Username: mostfamoh" -ForegroundColor Gray
    Write-Host "   → Password: votre mot de passe ou token" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Le dépôt existe déjà avec du contenu?" -ForegroundColor White
    Write-Host "   → Exécutez: git pull origin main --allow-unrelated-histories" -ForegroundColor Cyan
    Write-Host "   → Puis: git push -u origin main" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
pause
