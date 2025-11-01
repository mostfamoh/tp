# 🛡️ Guide du Système de Protection des Comptes

## Vue d'ensemble

Le système de protection des comptes limite les tentatives de connexion pour ralentir considérablement les attaques par force brute et dictionnaire.

## 🎯 Fonctionnalités

### Protection Automatique
- **Limite de tentatives**: Maximum 3 tentatives de mot de passe incorrect
- **Durée de verrouillage**: 30 minutes après le dépassement de la limite
- **Activation facultative**: Chaque utilisateur peut activer/désactiver sa protection
- **Déverrouillage manuel**: Possibilité de déverrouiller le compte à tout moment

### Statistiques en Temps Réel
- Nombre de tentatives échouées
- Statut du compte (actif/verrouillé)
- Temps restant avant déverrouillage automatique
- Historique de la dernière tentative échouée

## 📱 Utilisation Frontend

### Onglet Protection

1. **Accéder à l'onglet "🛡️ Protection"**
   - Connectez-vous d'abord (onglet "🔑 Connexion")
   - Naviguez vers l'onglet "Protection"

2. **Activer la protection**
   - Cliquez sur le bouton "Activer"
   - Le statut passe à "🟢 Activée"

3. **Consulter les statistiques**
   - Tentatives échouées: X/3
   - Statut du compte: ✅ Actif ou 🔒 Verrouillé
   - Temps restant si verrouillé

4. **Déverrouiller manuellement**
   - Si le compte est verrouillé
   - Cliquez sur "Déverrouiller maintenant"

## 🔧 API Endpoints

### 1. Activer/Désactiver la Protection

```http
POST /api/users/<username>/toggle-protection/
Content-Type: application/json

{
  "enabled": true
}
```

**Réponse:**
```json
{
  "success": true,
  "username": "john",
  "protection_enabled": true,
  "message": "Protection activée pour john"
}
```

### 2. Consulter le Statut

```http
GET /api/users/<username>/protection-status/
```

**Réponse:**
```json
{
  "username": "john",
  "protection_enabled": true,
  "failed_attempts": 2,
  "is_locked": false,
  "remaining_minutes": 0,
  "last_failed_attempt": "2025-10-31T21:15:30.123456Z"
}
```

### 3. Déverrouiller un Compte

```http
POST /api/users/<username>/unlock/
```

**Réponse:**
```json
{
  "success": true,
  "username": "john",
  "message": "Compte john déverrouillé avec succès"
}
```

### 4. Connexion (comportement modifié)

```http
POST /api/login/
Content-Type: application/json

{
  "username": "john",
  "password": "test123"
}
```

**Réponse (succès):**
```json
{
  "message": "Welcome back john!",
  "username": "john",
  "algorithm": "caesar",
  "success": true,
  "protection_enabled": true
}
```

**Réponse (mot de passe incorrect avec protection):**
```json
{
  "error": "Mot de passe incorrect. Il vous reste 2 tentative(s).",
  "attempts_left": 2
}
```

**Réponse (compte verrouillé):**
```json
{
  "error": "Compte verrouillé",
  "message": "Votre compte est verrouillé pour 28 minute(s) suite à trop de tentatives échouées.",
  "locked": true,
  "remaining_minutes": 28
}
```

## 💻 Utilisation Programmatique (Python)

### Exemple avec requests

```python
import requests

BASE_URL = 'http://127.0.0.1:8000/api'

# 1. Activer la protection
def activate_protection(username):
    url = f'{BASE_URL}/users/{username}/toggle-protection/'
    response = requests.post(url, json={'enabled': True})
    return response.json()

# 2. Vérifier le statut
def check_status(username):
    url = f'{BASE_URL}/users/{username}/protection-status/'
    response = requests.get(url)
    return response.json()

# 3. Déverrouiller
def unlock_account(username):
    url = f'{BASE_URL}/users/{username}/unlock/'
    response = requests.post(url)
    return response.json()

# Exemple d'utilisation
username = 'test_user'

# Activer
result = activate_protection(username)
print(f"Protection: {result['protection_enabled']}")

# Vérifier
status = check_status(username)
print(f"Tentatives: {status['failed_attempts']}/3")
print(f"Verrouillé: {status['is_locked']}")

# Déverrouiller si nécessaire
if status['is_locked']:
    unlock_account(username)
```

## 🔬 Tests

### Test Unitaire (modèle)

```bash
python test_protection_model.py
```

Ce script teste:
- ✅ Activation/désactivation de la protection
- ✅ Enregistrement des tentatives échouées
- ✅ Verrouillage après 3 tentatives
- ✅ Calcul du temps restant
- ✅ Déverrouillage manuel
- ✅ Comportement sans protection

### Test d'Intégration (API)

```bash
python test_protection.py
```

Ce script teste:
- ✅ Création d'utilisateur
- ✅ Tentatives sans protection (aucun verrouillage)
- ✅ Activation de la protection
- ✅ Tentatives avec protection (verrouillage après 3)
- ✅ Déverrouillage via API
- ✅ Connexion réussie (réinitialisation du compteur)

## 📊 Impact sur les Attaques

### Sans Protection

| Type d'attaque | Temps estimé |
|---------------|--------------|
| Dictionnaire (1000 mots) | ~5 secondes |
| Dictionnaire (1M mots) | ~5 secondes |
| Force brute (3 chars) | ~0.5 seconde |
| Force brute (6 chars) | ~quelques minutes |

### Avec Protection (3 tentatives / 30 min)

| Type d'attaque | Temps estimé |
|---------------|--------------|
| Dictionnaire (1000 mots) | **~5.5 jours** |
| Dictionnaire (1M mots) | **~15 000 ans** |
| Force brute (3 chars) | **~2.5 jours** |
| Force brute (6 chars) | **Impossible** |

**Calcul:**
- 3 tentatives / 30 minutes = 6 tentatives / heure
- 1000 mots / 6 = 166 heures = ~7 jours
- 1 000 000 mots / 6 = 166 666 heures = ~19 ans

### Impact sur les Attaques Automatisées

```python
# Sans protection: ~1000 tentatives/seconde
# Avec protection: ~0.0016 tentative/seconde (6/heure)

# Ralentissement: 625 000x
```

## 🎨 Interface Utilisateur

### États Visuels

1. **Protection Désactivée** (🟡)
   - Fond jaune clair
   - Bouton "Activer" visible
   - Avertissement de risque

2. **Protection Activée - Compte Actif** (🟢)
   - Fond vert clair
   - Statistiques affichées
   - Bouton "Désactiver" visible

3. **Protection Activée - Compte Verrouillé** (🔒)
   - Fond rouge clair
   - Temps restant affiché
   - Bouton "Déverrouiller maintenant"

### Messages Informatifs

```
📊 Statistiques
• Tentatives échouées: 2/3
• Statut du compte: ✅ Actif

⚠️ Compte verrouillé pour 28 minute(s)
Trop de tentatives de connexion échouées détectées.
[Déverrouiller maintenant]
```

## 🔐 Sécurité

### Points Forts
- ✅ Ralentissement drastique des attaques automatisées
- ✅ Protection contre les attaques par dictionnaire
- ✅ Protection contre la force brute
- ✅ Notification des tentatives suspectes
- ✅ Traçabilité (timestamp de dernière tentative)

### Limitations
- ⚠️ Le verrouillage peut être contourné par déverrouillage manuel
- ⚠️ Pas de notification par email/SMS
- ⚠️ Pas de blocage d'IP
- ⚠️ Pas de captcha après tentatives

### Améliorations Possibles
1. Ajouter un système de notification
2. Implémenter un blocage d'IP après plusieurs comptes bloqués
3. Augmenter progressivement la durée de verrouillage
4. Ajouter un captcha après la première tentative échouée
5. Enregistrer l'adresse IP des tentatives échouées

## 📝 Modèle de Données

```python
class CustomUser(models.Model):
    # Champs existants
    username = models.CharField(max_length=100, unique=True)
    password_encypted = models.CharField()
    algorithm = models.CharField(...)
    key_data = models.JSONField()
    
    # Nouveaux champs de protection
    protection_enabled = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    last_failed_attempt = models.DateTimeField(null=True, blank=True)
```

### Méthodes du Modèle

```python
# Vérifier si le compte est verrouillé
user.is_account_locked() -> bool

# Enregistrer une tentative échouée (verrouille après 3)
user.record_failed_attempt() -> None

# Réinitialiser les tentatives (après connexion réussie)
user.reset_failed_attempts() -> None

# Obtenir le temps restant de verrouillage (en minutes)
user.get_lock_remaining_time() -> int
```

## 🚀 Migration

La migration `0002_customuser_account_locked_until_and_more.py` ajoute les champs:
- `protection_enabled` (BooleanField, default=False)
- `failed_login_attempts` (IntegerField, default=0)
- `account_locked_until` (DateTimeField, nullable)
- `last_failed_attempt` (DateTimeField, nullable)

```bash
# Appliquer la migration
python manage.py migrate
```

## 📖 Exemples d'Utilisation

### Scénario 1: Activer la Protection

```javascript
// Frontend (React)
import { protectionService } from '../services/api';

const activateProtection = async () => {
  try {
    const result = await protectionService.toggleProtection('john', true);
    console.log(result.message);
    // "Protection activée pour john"
  } catch (error) {
    console.error(error);
  }
};
```

### Scénario 2: Gérer le Verrouillage

```python
# Backend (Django)
from crypto_lab.models import CustomUser

user = CustomUser.objects.get(username='john')

if user.is_account_locked():
    remaining = user.get_lock_remaining_time()
    print(f"Compte verrouillé pour {remaining} minutes")
    
    # Déverrouiller si nécessaire
    user.reset_failed_attempts()
```

### Scénario 3: Surveiller les Tentatives

```python
# Script de monitoring
import time
from crypto_lab.models import CustomUser

while True:
    users = CustomUser.objects.filter(
        protection_enabled=True,
        failed_login_attempts__gte=2
    )
    
    for user in users:
        print(f"⚠️  {user.username}: {user.failed_login_attempts} tentatives")
        if user.is_account_locked():
            print(f"   🔒 Verrouillé pour {user.get_lock_remaining_time()} min")
    
    time.sleep(60)  # Vérifier chaque minute
```

## 🎓 Démonstration

Pour une démonstration complète du système:

1. Lancez les serveurs:
```bash
# Terminal 1: Backend
python manage.py runserver 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

2. Accédez à l'interface: http://localhost:3000

3. Suivez le workflow:
   - Créez un utilisateur (Onglet "📝 Inscription")
   - Connectez-vous (Onglet "🔑 Connexion")
   - Activez la protection (Onglet "🛡️ Protection")
   - Testez avec de mauvais mots de passe
   - Observez le verrouillage après 3 tentatives

## 📞 Support

Pour toute question ou problème:
- Consultez la documentation complète
- Vérifiez les logs Django
- Exécutez les scripts de test
- Consultez le code source commenté

---

**Version**: 1.0  
**Date**: 31 Octobre 2025  
**Projet**: Crypto Lab - TP SSAD USTHB
