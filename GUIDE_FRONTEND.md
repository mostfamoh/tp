# 🚀 GUIDE RAPIDE - DÉMARRAGE DU FRONTEND

## ✅ Prérequis
- Django serveur en cours : `python manage.py runserver 127.0.0.1:8000`
- Node.js installé

## 🎯 Étapes pour démarrer le frontend

### 1. Ouvrir un nouveau terminal PowerShell

### 2. Aller dans le dossier frontend
```powershell
cd frontend
```

### 3. Installer les dépendances (si première fois)
```powershell
npm install
```

### 4. Démarrer le serveur de développement
```powershell
npm run dev
```

Le frontend sera disponible sur : **http://localhost:3000**

## 📝 Test de l'attaque dictionnaire

1. Ouvrir le navigateur : http://localhost:3000
2. Aller dans la section "Attaques"
3. Entrer le nom d'utilisateur : `bellia`
4. Cliquer sur "📚 Attaque Dictionnaire"
5. Résultat attendu : **✅ Mot de passe trouvé : 122**

## 🐛 Problèmes courants

### Erreur CORS
- ✅ RÉSOLUE : Le proxy Vite est configuré dans `vite.config.js`

### Erreur "Dictionary not found"
- ✅ RÉSOLUE : L'API charge maintenant `backend/dic.txt` automatiquement

### Erreur "User not authorized"
- Vérifier que l'utilisateur est dans `test_users.txt`
- Ajouter manuellement si nécessaire : `echo bellia >> test_users.txt`

## 📊 Utilisateurs de test disponibles

| Username | Mot de passe | Description |
|----------|--------------|-------------|
| `bellia` | `122` | 3 caractères {0,1,2} |
| `cas1_012` | `012` | 3 caractères {0,1,2} |
| `cas2_123456` | `123456` | 6 chiffres {0-9} |
| `cas3_complex` | `aB3@x9` | Alphanumérique + spéciaux |

## ✅ Vérification rapide

Test API direct (sans frontend) :
```powershell
python test_api_attack.py
```

Résultat attendu : Mot de passe `122` trouvé pour l'utilisateur `bellia`
