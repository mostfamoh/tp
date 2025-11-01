# 📚 Documentation : Stéganographie

## 🎯 Vue d'Ensemble

La **stéganographie** est l'art de cacher des messages secrets dans d'autres contenus (texte, images, audio, vidéo). Contrairement à la cryptographie qui rend le message illisible, la stéganographie cache **l'existence même** du message.

---

## 📝 Stéganographie dans le Texte

### Méthodes Disponibles

#### 1. **WhiteSpace** (Espaces et Tabulations)
- **Principe** : Encode le message en utilisant des espaces et des tabulations
- **Encodage** : `0 = espace`, `1 = tabulation`
- **Visibilité** : Invisible à l'œil nu
- **Robustesse** : Faible (sensible au formatage)
- **Capacité** : Illimitée

**Exemple :**
```python
Texte original : "Bonjour le monde."
Message secret : "HI"
Texte stégano : "Bonjour le monde.[espaces et tabs invisibles]"
```

#### 2. **Zero-Width Characters** (Caractères Unicode Invisibles)
- **Principe** : Utilise des caractères Unicode de largeur nulle
- **Caractères** : 
  - `U+200B` (Zero Width Space)
  - `U+200C` (Zero Width Non-Joiner)
  - `U+200D` (Zero Width Joiner)
- **Visibilité** : Totalement invisible
- **Robustesse** : Moyenne
- **Capacité** : Élevée

#### 3. **Case-Based** (Casse des Lettres) ✅ **LA PLUS FIABLE**
- **Principe** : Encode le message dans les majuscules/minuscules
- **Encodage** : `Majuscule = 1`, `minuscule = 0`
- **Visibilité** : Partiellement visible (mais naturel)
- **Robustesse** : Élevée
- **Capacité** : Limitée par le nombre de lettres

**Exemple :**
```
Message secret : "HI" = 01001000 01001001 (en binaire)
Texte original : "la cryptographie est fascinante..."
Texte stégano : "lA cRyptOgrAphIe eSt fasCinante..."
                 ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑
                 (casse modifiée selon les bits)
```

### Utilisation via API

#### Cacher un Message

```bash
POST /api/stego/text/hide/
Content-Type: application/json

{
  "cover_text": "Le texte qui servira de couverture...",
  "secret_message": "SECRET",
  "method": "case"
}
```

**Réponse :**
```json
{
  "stego_text": "Le Texte qui ServirA de couverturE...",
  "method": "case",
  "cover_length": 45,
  "secret_length": 6,
  "letters_used": 48,
  "explanation": "Message caché dans la casse des lettres"
}
```

#### Extraire un Message

```bash
POST /api/stego/text/extract/
Content-Type: application/json

{
  "stego_text": "Le Texte qui ServirA de couverturE...",
  "method": "case"
}
```

**Réponse :**
```json
{
  "secret_message": "SECRET",
  "method": "case",
  "success": true,
  "binary_length": 48
}
```

### Analyser un Texte de Couverture

```bash
POST /api/stego/analyze/text/
Content-Type: application/json

{
  "text": "Votre texte à analyser..."
}
```

**Réponse :**
```json
{
  "total_length": 336,
  "letters": 258,
  "words": 44,
  "sentences": 4,
  "capacity_case": 32,
  "capacity_whitespace": "unlimited",
  "capacity_zerowidth": "unlimited"
}
```

---

## 🖼️ Stéganographie dans les Images

### Méthode LSB (Least Significant Bit)

- **Principe** : Modifie le bit de poids faible de chaque composante RGB des pixels
- **Encodage** : Cache 1 bit par composante de couleur (R, G, B)
- **Visibilité** : Invisible à l'œil nu (différence ≤ 1 par pixel)
- **Robustesse** : Faible (sensible aux compressions JPEG)
- **Capacité** : Élevée (3 bits par pixel)
- **Qualité** : Perte négligeable

**Principe Technique :**
```
Pixel original : R=255, G=128, B=64
En binaire :     11111111, 10000000, 01000000

Message : "A" = 01000001 (binaire)

Modification LSB :
R: 11111111 → 11111110 (LSB changé à 0)
G: 10000000 → 10000001 (LSB changé à 1)
B: 01000000 → 01000000 (LSB à 0)
...

Pixel modifié : R=254, G=129, B=64
Différence imperceptible !
```

### Capacité d'une Image

Pour une image de **400×300 pixels** en RGB :
- **Pixels totaux** : 120,000
- **Bits disponibles** : 360,000 (3 par pixel)
- **Capacité max** : 45,000 caractères
- **Recommandé** : 22,500 caractères (50% de capacité)

### Utilisation via API

#### Cacher un Message dans une Image

```bash
POST /api/stego/image/hide/
Content-Type: application/json

{
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "secret_message": "This is a secret!",
  "method": "lsb"
}
```

**Réponse :**
```json
{
  "stego_image": "iVBORw0KGgoAAAANS... (base64)",
  "method": "lsb",
  "message_length": 17,
  "pixels_used": 648,
  "image_size": "400x300",
  "capacity": 360000,
  "usage_percent": 0.18,
  "explanation": "Message caché dans les LSB des pixels RGB"
}
```

#### Extraire un Message d'une Image

```bash
POST /api/stego/image/extract/
Content-Type: application/json

{
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "method": "lsb"
}
```

**Réponse :**
```json
{
  "secret_message": "This is a secret!",
  "method": "lsb",
  "success": true,
  "extracted_length": 17,
  "expected_length": 17
}
```

### Analyser la Capacité d'une Image

```bash
POST /api/stego/analyze/image/
Content-Type: application/json

{
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS..."
}
```

**Réponse :**
```json
{
  "width": 400,
  "height": 300,
  "channels": 3,
  "format": "PNG",
  "mode": "RGB",
  "total_pixels": 120000,
  "total_bits": 360000,
  "max_characters": 45000,
  "max_characters_kb": 43.95,
  "recommended_message_length": 22500
}
```

### Créer une Image de Test

```bash
GET /api/stego/sample-image/?width=400&height=300
```

**Réponse :**
```json
{
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "width": 400,
  "height": 300
}
```

---

## 🔗 Endpoints API Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/stego/text/hide/` | POST | Cacher un message dans du texte |
| `/api/stego/text/extract/` | POST | Extraire un message du texte |
| `/api/stego/image/hide/` | POST | Cacher un message dans une image |
| `/api/stego/image/extract/` | POST | Extraire un message d'une image |
| `/api/stego/methods/` | GET | Liste des méthodes disponibles |
| `/api/stego/analyze/text/` | POST | Analyser la capacité d'un texte |
| `/api/stego/analyze/image/` | POST | Analyser la capacité d'une image |
| `/api/stego/sample-image/` | GET | Créer une image de test |

---

## 🎓 Cas d'Usage Pédagogiques

### 1. Communication Discrète

**Scénario** : Alice veut envoyer un message secret à Bob sans éveiller les soupçons.

```python
# Alice cache le message
cover = "Rendez-vous demain à la bibliothèque pour étudier."
secret = "15h"
stego = hide_text_in_text(cover, secret, method='case')

# Texte envoyé (apparemment innocent)
# "ReNdez-VoUs deMaiN à lA bibliothèque..."

# Bob extrait le message
message = extract_text_from_text(stego, method='case')
# Résultat : "15h"
```

### 2. Protection de Propriété Intellectuelle

**Scénario** : Marquer une image avec un copyright invisible.

```python
image = load_image("photo.png")
copyright = "© 2025 John Doe - ID:12345"
stego_image = hide_text_in_image(image, copyright, method='lsb')

# L'image semble identique mais contient la signature
# En cas de litige, on peut extraire le copyright
```

### 3. Comparaison des Méthodes

```
Texte : "La cryptographie est fascinante"
Message secret : "HI"

┌─────────────┬──────────────┬─────────────┬──────────────┐
│ Méthode     │ Visible ?    │ Robuste ?   │ Capacité     │
├─────────────┼──────────────┼─────────────┼──────────────┤
│ WhiteSpace  │ Non          │ Faible      │ Illimitée    │
│ Zero-Width  │ Non          │ Moyenne     │ Élevée       │
│ Case-Based  │ Partiellement│ Élevée      │ Limitée      │
└─────────────┴──────────────┴─────────────┴──────────────┘

Recommandation : Case-Based pour fiabilité
```

---

## 🧪 Tests

### Test Automatisé

```bash
python test_steganography.py
```

**Résultats :**
```
✅ Méthode Case-Based (texte) : 100% réussi
✅ Méthode LSB (image) : 100% réussi
✅ Analyse de capacité : Fonctionnel
✅ Extraction de messages : Fonctionnel
```

### Test Manuel via curl

```bash
# Cacher un message dans du texte
curl -X POST http://localhost:8000/api/stego/text/hide/ \
  -H "Content-Type: application/json" \
  -d '{
    "cover_text": "Hello World from Paris",
    "secret_message": "HI",
    "method": "case"
  }'

# Extraire le message
curl -X POST http://localhost:8000/api/stego/text/extract/ \
  -H "Content-Type: application/json" \
  -d '{
    "stego_text": "HEllo WorLd frOm pariS",
    "method": "case"
  }'
```

---

## 🔐 Sécurité et Limitations

### Avantages de la Stéganographie

✅ **Discrétion** : L'existence du message est cachée
✅ **Double protection** : Peut être combinée avec le chiffrement
✅ **Pas de suspicion** : Le contenu semble normal

### Limitations

❌ **Robustesse** : Sensible aux modifications (compression, redimensionnement)
❌ **Capacité limitée** : Dépend de la taille du support
❌ **Détection** : Des outils d'analyse stéganographique existent

### Bonnes Pratiques

1. **Toujours chiffrer** le message avant de le cacher
   ```
   Message → Chiffrement (AES) → Stéganographie → Support
   ```

2. **Ne pas saturer** la capacité (max 50%)
3. **Utiliser des formats non compressés** (PNG plutôt que JPEG)
4. **Tester l'extraction** avant de transmettre

---

## 📊 Comparaison : Cryptographie vs Stéganographie

```
┌────────────────────────────────────────────────────────┐
│                  CRYPTOGRAPHIE                         │
│  Message visible mais illisible                        │
│                                                        │
│  "Bonjour" → "Xjajhz" (César +15)                     │
│                                                        │
│  ⚠️  On sait qu'il y a un secret                       │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                 STÉGANOGRAPHIE                         │
│  Message invisible dans un support anodin             │
│                                                        │
│  "Bonjour" → "La CrypTogrAphIe eSt FascInante"        │
│               (message caché dans la casse)           │
│                                                        │
│  ✅ Personne ne soupçonne l'existence du secret        │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│              STÉGANO-CRYPTOGRAPHIE                     │
│  Message chiffré ET caché = Double sécurité           │
│                                                        │
│  "Bonjour" → Chiffrement → "Xjajhz"                   │
│           → Stéganographie → "La CrypTo..."           │
│                                                        │
│  ✅✅ Sécurité maximale                                 │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Pour Aller Plus Loin

### Combinaison avec la Cryptographie

```python
# 1. Chiffrer le message
from backend.cryptotoolbox import encrypt_with_algorithm

secret = "Rendez-vous 15h"
key = {'shift': 3}
encrypted = encrypt_with_algorithm('caesar', secret, key)
# Résultat : "UHQGHCYRXV 15K"

# 2. Cacher dans une image
stego_image = hide_text_in_image(image, encrypted, method='lsb')

# 3. Pour lire : extraire puis déchiffrer
extracted = extract_text_from_image(stego_image, method='lsb')
decrypted = decrypt_with_algorithm('caesar', extracted, key)
# Résultat : "Rendez-vous 15h"
```

### Applications Réelles

1. **Watermarking** : Marquer les images avec des métadonnées
2. **DRM** : Protéger la propriété intellectuelle
3. **Communication secrète** : Messagerie discrète
4. **Forensics** : Cacher des preuves numériques

---

## 📚 Ressources

### Documentation Technique

- **Modules** : `backend/cryptotoolbox/steganography/`
  - `text_stego.py` : Stéganographie texte
  - `image_stego.py` : Stéganographie image

- **Tests** : `test_steganography.py`

### Bibliothèques Utilisées

- **Pillow** : Traitement d'images
- **NumPy** : Manipulation de pixels
- **Django** : API REST

---

**Date : 31 Octobre 2025**  
**Version : 1.0**  
**Status : ✅ Fonctionnel et testé**
