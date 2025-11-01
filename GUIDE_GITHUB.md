# 🚀 GUIDE: Pousser le Projet vers GitHub

## Méthode 1: Commandes Manuelles (Recommandé)

Ouvrez PowerShell dans le dossier du projet et exécutez les commandes suivantes:

### Étape 1: Initialiser Git

```powershell
cd C:\Users\j\OneDrive\Desktop\ssad_tp1
git init
```

### Étape 2: Ajouter le remote

```powershell
git remote add origin https://github.com/mostfamoh/tp.git
```

Si vous avez déjà un remote, supprimez-le d'abord:
```powershell
git remote remove origin
git remote add origin https://github.com/mostfamoh/tp.git
```

### Étape 3: Ajouter tous les fichiers

```powershell
git add .
```

### Étape 4: Créer un commit

```powershell
git commit -m "Initial commit - Crypto Lab TP SSAD USTHB"
```

### Étape 5: Push vers GitHub

```powershell
git branch -M main
git push -u origin main
```

**Note**: Vous serez invité à entrer vos identifiants GitHub.

---

## Méthode 2: Si vous avez l'authentification 2FA

Si vous avez l'authentification à deux facteurs activée sur GitHub, vous devez créer un **Personal Access Token**:

### Créer un Token

1. Allez sur: https://github.com/settings/tokens
2. Cliquez sur "Generate new token" → "Generate new token (Classic)"
3. Donnez un nom au token (ex: "TP SSAD")
4. Sélectionnez le scope **"repo"** (cochez toutes les cases sous repo)
5. Cliquez sur "Generate token"
6. **COPIEZ LE TOKEN** (vous ne pourrez plus le voir après!)

### Utiliser le Token

Lors du push, utilisez:
- **Username**: `mostfamoh`
- **Password**: `votre_token_copié` (PAS votre mot de passe!)

---

## Méthode 3: Commande tout-en-un

Copiez-collez toutes ces commandes d'un coup:

```powershell
cd C:\Users\j\OneDrive\Desktop\ssad_tp1
git init
git remote remove origin 2>$null
git remote add origin https://github.com/mostfamoh/tp.git
git add .
git commit -m "Initial commit - Crypto Lab TP SSAD USTHB - Complete project"
git branch -M main
git push -u origin main
```

---

## ⚠️ Problèmes Courants

### Problème 1: "repository not found"

**Solution**: Vérifiez que le dépôt existe sur GitHub
- Allez sur: https://github.com/mostfamoh/tp
- Si le dépôt n'existe pas, créez-le d'abord:
  1. Allez sur https://github.com/new
  2. Repository name: `tp`
  3. Cochez "Private" ou "Public" selon votre choix
  4. **NE COCHEZ PAS** "Initialize this repository with a README"
  5. Cliquez "Create repository"

### Problème 2: "failed to push some refs"

**Solution 1**: Le dépôt distant a déjà du contenu
```powershell
git pull origin main --allow-unrelated-histories
git push -u origin main
```

**Solution 2**: Forcer le push (⚠️ ATTENTION: écrase tout sur GitHub)
```powershell
git push -u origin main --force
```

### Problème 3: "authentication failed"

**Solution**: Utilisez un Personal Access Token (voir Méthode 2 ci-dessus)

### Problème 4: Fichier trop volumineux

Si Git refuse `dict_digits6.txt` (7.63 MB):

```powershell
# Ajouter au .gitignore
echo "backend/dictionaries/dict_digits6.txt" >> .gitignore

# Réinitialiser et recommencer
git rm --cached backend/dictionaries/dict_digits6.txt
git add .
git commit -m "Remove large dictionary file"
git push -u origin main
```

---

## ✅ Vérification

Une fois le push réussi, vérifiez:

1. Allez sur: https://github.com/mostfamoh/tp
2. Vous devriez voir tous vos fichiers
3. Partagez le lien avec votre professeur!

---

## 📝 Commandes Git Utiles

### Voir l'état actuel
```powershell
git status
```

### Voir l'historique des commits
```powershell
git log --oneline
```

### Voir les fichiers qui seront commitées
```powershell
git diff --cached --name-only
```

### Annuler le dernier commit (garder les changements)
```powershell
git reset --soft HEAD~1
```

### Mettre à jour depuis GitHub
```powershell
git pull origin main
```

---

## 🎓 Après le Push

Une fois votre projet sur GitHub, vous pouvez:

1. **Le cloner ailleurs**:
   ```powershell
   git clone https://github.com/mostfamoh/tp.git
   ```

2. **Créer une branche pour les modifications**:
   ```powershell
   git checkout -b ameliorations
   git add .
   git commit -m "Ajout de nouvelles fonctionnalités"
   git push origin ameliorations
   ```

3. **Mettre à jour votre version locale**:
   ```powershell
   git pull origin main
   ```

---

## 💡 Conseil Pro

Créez un fichier `.gitattributes` pour gérer les fins de ligne:

```powershell
echo "* text=auto" > .gitattributes
echo "*.py text eol=lf" >> .gitattributes
echo "*.js text eol=lf" >> .gitattributes
echo "*.jsx text eol=lf" >> .gitattributes
git add .gitattributes
git commit -m "Add .gitattributes"
git push
```

---

Bon push ! 🚀
