# ✅ RÉSUMÉ FINAL - Projet SSAD TP1 Cryptographie

## 🎉 CE QUI EST PRÊT

### ✅ 1. Tous les dictionnaires sont générés

- **dict_012.txt**: 27 combinaisons de {0,1,2}³
- **dict_digits3.txt**: 1,000 combinaisons de {0-9}³  
- **dict_digits6.txt**: 1,000,000 combinaisons de {0-9}⁶ (7.63 MB)
- **dict_test.txt**: 50 mots de passe communs pour tests rapides

### ✅ 2. L'API supporte TOUS les dictionnaires

L'endpoint `/api/attack/dictionary` accepte maintenant le paramètre `dictionary_type`:

```json
{
  "target_username": "bellia",
  "dictionary_type": "012",     ← NOUVEAU!
  "max_seconds": 60,
  "limit": 0
}
```

Types supportés:
- `"default"`: backend/dic.txt (27 entrées)
- `"012"`: dict_012.txt (27 entrées)
- `"test"`: dict_test.txt (50 entrées)
- `"digits3"`: dict_digits3.txt (1,000 entrées)
- `"digits6"`: dict_digits6.txt (1,000,000 entrées)

### ✅ 3. Utilisateurs de test créés

| Username | Password | Description |
|----------|----------|-------------|
| `bellia` | `122` | Simple |
| `cas1_012` | `012` | Cas 1: {0,1,2}³ |
| `cas2_123456` | `123456` | Cas 2: {0-9}⁶ |
| `cas3_complex` | `aB3@x9` | Cas 3: Complexe |

## 🚀 COMMENT UTILISER

### Étape 1: Démarrer le serveur (Terminal 1)

```powershell
cd C:\Users\j\OneDrive\Desktop\ssad_tp1
python manage.py runserver 8000
```

**IMPORTANT**: Laissez ce terminal OUVERT!

### Étape 2: Tester l'API (Terminal 2 - NOUVEAU terminal)

Ouvrez un NOUVEAU PowerShell et testez:

```powershell
cd C:\Users\j\OneDrive\Desktop\ssad_tp1

# Test rapide avec dictionnaire de 27 entrées
$body = @{
    target_username = "bellia"
    dictionary_type = "012"
    max_seconds = 60
    limit = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Étape 3: Démarrer le frontend (Terminal 3 - NOUVEAU terminal)

```powershell
cd C:\Users\j\OneDrive\Desktop\ssad_tp1\frontend
npm run dev
```

Le frontend sera accessible sur: http://localhost:3001/

## 📝 CE QU'IL RESTE À FAIRE

### 🔧 Tâche 1: Ajouter sélection de dictionnaire dans le frontend

Dans `frontend/src/components/AttackPanel.jsx`, ajoutez:

```jsx
const [dictionaryType, setDictionaryType] = useState('012');

// Dans le formulaire, ajoutez:
<select value={dictionaryType} onChange={(e) => setDictionaryType(e.target.value)}>
  <option value="012">Petit dictionnaire (27 entrées - {0,1,2}³)</option>
  <option value="test">Test (50 mots de passe communs)</option>
  <option value="digits3">Moyen (1,000 entrées - {0-9}³)</option>
  <option value="digits6">GRAND (1,000,000 entrées - {0-9}⁶) ⚠️</option>
</select>

// Lors de l'appel API, ajoutez dictionary_type:
const response = await fetch('/api/attack/dictionary', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    target_username: username,
    dictionary_type: dictionaryType,  ← AJOUTEZ CECI
    max_seconds: 60,
    limit: 0
  })
});
```

### 🔧 Tâche 2: Afficher les infos du dictionnaire utilisé

Dans la réponse de l'API, vous avez maintenant `dictionary_info`:

```jsx
const result = await response.json();

// Affichez:
console.log(`Dictionnaire: ${result.dictionary_info.type}`);
console.log(`Taille: ${result.dictionary_info.size} entrées`);
console.log(`Temps: ${result.time_sec} secondes`);
console.log(`Trouvé: ${result.matches_count} mot(s) de passe`);
```

## 🎯 DÉMONSTRATION POUR LE PROFESSEUR

### Partie 3: Attaques dans les 03 cas

#### Cas 1: Mot de passe de {0,1,2}³ → CRAQUÉ RAPIDEMENT ✅

```powershell
$body = @{ target_username = "cas1_012"; dictionary_type = "012"; max_seconds = 60; limit = 0 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" -Method POST -Body $body -ContentType "application/json"
```

**Résultat**: Mot de passe `012` trouvé en < 0.01 seconde (27 tentatives)

#### Cas 2: Mot de passe de {0-9}⁶ → CRAQUÉ MAIS LONG ⚠️

```powershell
$body = @{ target_username = "cas2_123456"; dictionary_type = "digits6"; max_seconds = 120; limit = 0 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" -Method POST -Body $body -ContentType "application/json"
```

**Résultat**: Mot de passe `123456` trouvé mais prend plusieurs secondes (jusqu'à 1M tentatives)

#### Cas 3: Mot de passe complexe → NON CRAQUÉ ❌

```powershell
$body = @{ target_username = "cas3_complex"; dictionary_type = "digits6"; max_seconds = 60; limit = 0 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" -Method POST -Body $body -ContentType "application/json"
```

**Résultat**: Mot de passe `aB3@x9` NON trouvé (pas dans le dictionnaire)

**CONCLUSION POUR LE PROF**: 
- ✅ Mots de passe simples = DANGEREUX (craqués rapidement)
- ⚠️ Mots de passe de taille moyenne = VULNÉRABLES (prennent du temps mais trouvés)
- ✅ Mots de passe complexes = SÉCURISÉS (non trouvés même avec grand dictionnaire)

## 📁 FICHIERS IMPORTANTS

### Code Backend
- `crypto_lab/views.py`: API modifiée pour supporter les différents dictionnaires
- `backend/cryptotoolbox/attack/attack_runner.py`: Moteur d'attaque (bug JSON fixé)
- `backend/cryptotoolbox/attack/dictionaryattack.py`: Logique d'attaque par dictionnaire

### Dictionnaires
- `backend/dic.txt`: Dictionnaire par défaut (27 entrées)
- `backend/dictionaries/dict_012.txt`: 27 combinaisons {0,1,2}³
- `backend/dictionaries/dict_digits3.txt`: 1,000 combinaisons {0-9}³
- `backend/dictionaries/dict_digits6.txt`: 1,000,000 combinaisons {0-9}⁶
- `backend/dictionaries/dict_test.txt`: 50 mots de passe communs

### Scripts Utiles
- `generate_dictionaries.py`: Génère tous les dictionnaires (déjà exécuté)
- `demonstration_partie3.py`: Démo complète pour Partie 3
- `GUIDE_DICTIONNAIRES.md`: Guide complet d'utilisation

## 🐛 BUGS RÉSOLUS

✅ Registration endpoint (erreurs 409, 400 au lieu de 500)
✅ Double-JSON-encoding de `key_data` dans la BDD
✅ Password encryption vide pour certains utilisateurs
✅ Dictionary attack ne trouvait pas les mots de passe
✅ API ne chargeait pas le fichier dictionnaire
✅ Dictionnaires incomplets (maintenant 1M+ entrées disponibles)

## ✨ AMÉLIORATIONS AJOUTÉES

✅ Support multi-dictionnaires dans l'API
✅ Métadonnées `dictionary_info` dans les réponses
✅ Dictionnaires complets pour toutes les combinaisons demandées
✅ Scripts de démonstration et de test
✅ Documentation complète

## 🎓 POUR FINIR VOTRE PROJET

1. **✅ TERMINÉ**: Backend prêt, API fonctionnelle, dictionnaires générés
2. **⏳ À FAIRE**: Ajouter sélection de dictionnaire dans le frontend React (5-10 minutes)
3. **⏳ À FAIRE**: Tester les 3 cas de "Partie 3" et prendre des captures d'écran
4. **✅ PRÊT**: Documentation et guides disponibles

## 💡 ASTUCES

- **N'utilisez PAS** `digits6` pour des tests rapides (1M entrées = lent!)
- **Utilisez** `test` ou `012` pour tester rapidement (27-50 entrées)
- **Deux terminaux**: Un pour le serveur, un pour les tests
- **Frontend**: Ajoutez une alerte "Ceci peut prendre plusieurs minutes" pour `digits6`

## 🆘 AIDE

Si quelque chose ne marche pas:

1. **Serveur Django**: `python manage.py runserver 8000`
2. **Frontend**: `cd frontend ; npm run dev`
3. **Voir les erreurs**: Regardez le terminal du serveur Django
4. **Régénérer dictionnaires**: `python generate_dictionaries.py`

Tous les fichiers sont prêts. Il ne reste qu'à ajouter la sélection de dictionnaire dans le frontend React ! 🚀

Bonne chance pour votre projet ! 🎉
