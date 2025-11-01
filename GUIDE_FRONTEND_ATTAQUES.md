# 🎯 GUIDE RAPIDE - Attaques sur le Frontend

## ✅ Modifications Effectuées

### 1. **Backend** (`crypto_lab/views.py`)
- ✅ Conversion automatique des chiffres en lettres lors de l'enregistrement
- ✅ Support des différents types de dictionnaires

### 2. **Frontend** (`AttackPanel.jsx` et `api.js`)
- ✅ Ajout d'un sélecteur de dictionnaire
- ✅ Passage du paramètre `dictionary_type` à l'API
- ✅ Affichage des informations du dictionnaire utilisé

## 🚀 Comment Utiliser

### Étape 1: Démarrer le Serveur Django

```powershell
# Terminal 1
python manage.py runserver 8000
```

### Étape 2: Démarrer le Frontend

```powershell
# Terminal 2 (nouveau terminal)
cd frontend
npm run dev
```

Le frontend sera accessible sur: **http://localhost:3000/**

### Étape 3: Créer un Utilisateur

1. Allez dans la section **"Enregistrement"**
2. Créez un utilisateur, par exemple:
   - Username: `test123`
   - Password: `123456`
   - Algorithm: `cesar`
   - Key: `3`

Le mot de passe `123456` sera automatiquement converti en `BCDEFG` puis chiffré.

### Étape 4: Attaquer l'Utilisateur

1. Allez dans la section **"Attaques"**
2. Entrez le username: `test123`
3. **IMPORTANT**: Sélectionnez le bon dictionnaire:
   - Pour `123456` → Choisir **"Grand - {0-9}⁶ (1,000,000 entrées)"**
   - Pour `012` → Choisir **"Petit - {0,1,2}³ (27 entrées)"**
   - Pour `111` → Choisir **"Petit - {0,1,2}³ (27 entrées)"**
4. Cliquez sur **"📚 Attaque Dictionnaire"**
5. Attendez le résultat (peut prendre 5-60 secondes pour le grand dictionnaire)

## 📋 Types de Dictionnaires

| Type | Taille | Utilisation | Temps |
|------|--------|-------------|-------|
| **012** | 27 entrées | Mots de passe {0,1,2}³ (000, 001, 012, 111, etc.) | < 0.01s |
| **test** | 50 entrées | Mots de passe communs (test rapide) | < 0.01s |
| **digits3** | 1,000 | Mots de passe {0-9}³ (000 à 999) | < 0.1s |
| **digits6** | 1,000,000 | Mots de passe {0-9}⁶ (000000 à 999999) | 5-60s |

## 🎯 Exemples de Test

### Test 1: Mot de passe simple
```
Username: user_simple
Password: 012
Algorithm: cesar
Key: 3
Dictionnaire: "Petit - {0,1,2}³"
Résultat: ✅ Trouvé en < 0.01s
```

### Test 2: Mot de passe moyen
```
Username: user_moyen
Password: 123456
Algorithm: cesar
Key: 3
Dictionnaire: "Grand - {0-9}⁶"
Résultat: ✅ Trouvé en ~5s (123,456 tentatives)
```

### Test 3: Mot de passe complexe
```
Username: user_complex
Password: aB3@x9
Algorithm: cesar
Key: 3
Dictionnaire: "Grand - {0-9}⁶"
Résultat: ❌ Non trouvé (pas dans le dictionnaire)
```

## ⚠️ Points Importants

1. **Choisir le BON dictionnaire** :
   - `012`, `111`, `222` → Dictionnaire `012`
   - `123`, `456`, `789` → Dictionnaire `digits3`
   - `123456`, `999999` → Dictionnaire `digits6`

2. **Le dictionnaire `digits6` est LENT** :
   - Contient 1 million d'entrées
   - Prend 5-60 secondes
   - Affiche "Attaque en cours..." pendant l'exécution

3. **Conversion automatique** :
   - Tous les mots de passe numériques sont convertis automatiquement
   - `0→A, 1→B, 2→C, 3→D, 4→E, 5→F, 6→G, 7→H, 8→I, 9→J`
   - Exemple: `123` devient `BCD` avant chiffrement

## 🐛 Dépannage

### Problème: "Aucun mot de passe trouvé"
**Solutions:**
1. Vérifiez que vous utilisez le **bon dictionnaire**
2. Pour `123456`, utilisez `digits6` (pas `digits3`)
3. Pour `012`, utilisez `012` (pas `digits6`)

### Problème: L'attaque est trop lente
**Solutions:**
1. Utilisez un dictionnaire plus petit pour tester
2. Le dictionnaire `digits6` prend normalement 5-60 secondes
3. Essayez avec `test` ou `012` pour des tests rapides

### Problème: Le frontend ne charge pas
**Solutions:**
1. Vérifiez que le serveur Django est démarré (port 8000)
2. Vérifiez que le frontend est démarré (port 3000)
3. Rechargez la page avec Ctrl+F5

## ✅ Vérification Rapide

Testez avec l'utilisateur **bellia** que vous avez créé:

1. Ouvrez le frontend: http://localhost:3000/
2. Section "Attaques"
3. Username: `bellia`
4. Dictionnaire: **"Grand - {0-9}⁶"**
5. Cliquez "Attaque Dictionnaire"
6. Résultat attendu: **Trouvé `123456` en ~5 secondes** ✅

Si ça fonctionne, tout est OK ! 🎉
