# Guide pour Tester les Dictionnaires d'Attaque

## ✅ ÉTAPE 1: Démarrer le serveur Django

```powershell
python manage.py runserver 8000
```

**Attendez** que vous voyiez:
```
Starting development server at http://127.0.0.1:8000/
```

## ✅ ÉTAPE 2: Dans une NOUVELLE fenêtre PowerShell, tester l'API

### Test 1: Dictionnaire par défaut (27 entrées - {0,1,2}³)

```powershell
$body = @{
    target_username = "bellia"
    dictionary_type = "default"
    max_seconds = 60
    limit = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Test 2: Dictionnaire {0,1,2}³ (27 entrées)

```powershell
$body = @{
    target_username = "cas1_012"
    dictionary_type = "012"
    max_seconds = 60
    limit = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Test 3: Dictionnaire de test (50 mots de passe communs)

```powershell
$body = @{
    target_username = "bellia"
    dictionary_type = "test"
    max_seconds = 60
    limit = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Test 4: Dictionnaire {0-9}³ (1,000 entrées)

```powershell
$body = @{
    target_username = "bellia"
    dictionary_type = "digits3"
    max_seconds = 60
    limit = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Test 5: GRAND Dictionnaire {0-9}⁶ (1,000,000 entrées) ⚠️

**ATTENTION**: Ce test peut prendre plusieurs minutes!

```powershell
$body = @{
    target_username = "cas2_123456"
    dictionary_type = "digits6"
    max_seconds = 120
    limit = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

## 📊 Interprétation des Résultats

La réponse JSON contient:

```json
{
  "target_username": "bellia",
  "algorithm": "caesar",
  "mode": "dictionary",
  "attempts": 27,
  "time_sec": 0.003,
  "matches_count": 1,
  "matches": [
    {
      "candidate_plaintext": "BCC",
      "candidate_key": {
        "password_candidate": "122"
      },
      "confidence": "high"
    }
  ],
  "dictionary_info": {
    "type": "default",
    "path": "C:\\Users\\j\\OneDrive\\Desktop\\ssad_tp1\\backend\\dic.txt",
    "size": 27
  }
}
```

### Clés importantes:

- **`dictionary_info`**: Informations sur le dictionnaire utilisé
  - `type`: Type de dictionnaire ('default', '012', 'digits3', 'digits6', 'test')
  - `size`: Nombre d'entrées dans le dictionnaire
  - `path`: Chemin absolu du fichier dictionnaire

- **`attempts`**: Nombre de tentatives (doit correspondre à la taille du dictionnaire)
- **`time_sec`**: Temps écoulé en secondes
- **`matches_count`**: Nombre de mots de passe trouvés
- **`matches`**: Liste des mots de passe trouvés avec détails

## 🎯 Utilisateurs de Test

| Username | Password | Algorithm | Shift | Encrypted | Description |
|----------|----------|-----------|-------|-----------|-------------|
| `bellia` | `122` | Caesar | 3 | `EFF` | Mot de passe simple |
| `cas1_012` | `012` | Caesar | 3 | `DEF` | Cas 1: {0,1,2}³ |
| `cas2_123456` | `123456` | Caesar | 5 | `GHIJKL` | Cas 2: {0-9}⁶ |
| `cas3_complex` | `aB3@x9` | Caesar | 7 | `DEGAM` | Cas 3: Complexe |

## 📁 Dictionnaires Disponibles

| Type | Fichier | Taille | Description |
|------|---------|--------|-------------|
| `default` | `backend/dic.txt` | 27 | {0,1,2}³ - Par défaut |
| `012` | `backend/dictionaries/dict_012.txt` | 27 | {0,1,2}³ |
| `test` | `backend/dictionaries/dict_test.txt` | 50 | Mots de passe communs |
| `digits3` | `backend/dictionaries/dict_digits3.txt` | 1,000 | {0-9}³ |
| `digits6` | `backend/dictionaries/dict_digits6.txt` | 1,000,000 | {0-9}⁶ (7.63 MB) |

## 🚀 Utilisation dans le Frontend

Le frontend React doit envoyer une requête POST à `/api/attack/dictionary` avec:

```javascript
const response = await fetch('http://localhost:8000/api/attack/dictionary', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    target_username: 'bellia',
    dictionary_type: 'digits3',  // 'default', '012', 'test', 'digits3', 'digits6'
    max_seconds: 60,
    limit: 0
  })
});

const result = await response.json();
console.log(`Trouvé ${result.matches_count} mot(s) de passe`);
console.log(`Dictionnaire: ${result.dictionary_info.type} (${result.dictionary_info.size} entrées)`);
```

## ⚡ Démonstration "Partie 3" pour le Professeur

### Cas 1: Mot de passe simple de {0,1,2}³ ✅

```powershell
# Attaquer 'cas1_012' avec mot de passe '012'
$body = @{ target_username = "cas1_012"; dictionary_type = "012"; max_seconds = 60; limit = 0 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" -Method POST -Body $body -ContentType "application/json"
```

**Résultat attendu**: Trouvé en < 0.01 seconde (27 tentatives)

### Cas 2: Mot de passe de {0-9}⁶ ⚠️

```powershell
# Attaquer 'cas2_123456' avec mot de passe '123456'
$body = @{ target_username = "cas2_123456"; dictionary_type = "digits6"; max_seconds = 120; limit = 0 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" -Method POST -Body $body -ContentType "application/json"
```

**Résultat attendu**: Trouvé mais prend plusieurs secondes (jusqu'à 1,000,000 tentatives)

### Cas 3: Mot de passe complexe ❌

```powershell
# Attaquer 'cas3_complex' avec mot de passe 'aB3@x9'
$body = @{ target_username = "cas3_complex"; dictionary_type = "digits6"; max_seconds = 60; limit = 0 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/attack/dictionary" -Method POST -Body $body -ContentType "application/json"
```

**Résultat attendu**: NON trouvé (mot de passe pas dans le dictionnaire)

## 🔧 Dépannage

### Erreur "Connection refused"
→ Le serveur Django n'est pas démarré. Exécutez: `python manage.py runserver 8000`

### Erreur 404 "Fichier dictionnaire introuvable"
→ Générez les dictionnaires: `python generate_dictionaries.py`

### Erreur 500 "Internal Server Error"
→ Vérifiez les logs du serveur Django dans le terminal

### Le serveur crash lors du test
→ N'exécutez PAS les scripts de test dans le même terminal que le serveur
→ Utilisez DEUX terminaux séparés: un pour le serveur, un pour les tests
