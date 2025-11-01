# ⚠️ Protection et Attaques Automatiques - Analyse

## 🔍 Question

**Que se passe-t-il si j'active la protection et que je lance une attaque par dictionnaire ou force brute ?**

## 🧪 Test Réalisé

```bash
python test_attack_protection_simple.py
```

### Résultats

| Scénario | Protection | Temps d'attaque | Compte bloqué ? |
|----------|-----------|-----------------|-----------------|
| Attaque sans protection | ❌ Désactivée | 5.99s | ❌ Non |
| Attaque avec protection | ✅ Activée | 5.86s | ❌ Non |

**Tentatives échouées enregistrées:** 0/3 (dans les deux cas)

## ⚠️ CONSTAT IMPORTANT

### La protection N'AFFECTE PAS les attaques automatiques ! 

**Pourquoi ?**

Les attaques par dictionnaire et force brute utilisent des endpoints différents du login:

```
Login manuel:     POST /api/login/              ✅ Protégé
Attaque dictionnaire: POST /api/attack/full_dictionary/  ❌ Non protégé
Attaque force brute:  POST /api/attack/full_bruteforce/  ❌ Non protégé
```

## 📊 Flux Technique

### Login Manuel (Protégé) ✅

```
Utilisateur → /api/login/
            ↓
    login_user(request)
            ↓
    is_account_locked() ? → Vérifie le verrouillage
            ↓
    decrypt_with_algorithm()
            ↓
    Mot de passe correct ?
      ├─ Oui → reset_failed_attempts()
      └─ Non → record_failed_attempt() → Verrouille après 3 tentatives
```

### Attaque Automatique (Non protégé) ❌

```
Script → /api/attack/full_dictionary/
       ↓
   api_attack_full_dictionary(request)
       ↓
   Charge le dictionnaire
       ↓
   Pour chaque mot:
     decrypt_with_algorithm()
     Compare avec le mot déchiffré
       ↓
   Retourne le résultat
   
❌ N'appelle JAMAIS login_user()
❌ N'appelle JAMAIS record_failed_attempt()
❌ Ne vérifie JAMAIS is_account_locked()
```

## 🎯 Conséquences

### Ce qui EST protégé ✅
- ✅ Tentatives de connexion manuelles via l'interface
- ✅ Tentatives via l'endpoint `/api/login/`
- ✅ Scripts qui utilisent l'API de login

### Ce qui N'EST PAS protégé ❌
- ❌ Attaques par dictionnaire (`/api/attack/full_dictionary/`)
- ❌ Attaques par force brute (`/api/attack/full_bruteforce/`)
- ❌ Tous les scripts qui déchiffrent directement

## 💡 Pourquoi cette Architecture ?

Les endpoints d'attaque sont **pédagogiques** :
- Ils permettent de **tester** la sécurité des mots de passe
- Ils **démontrent** les techniques de cryptanalyse
- Ils sont utilisés pour **l'éducation**, pas la production

Dans un système réel, ces endpoints n'existeraient pas !

## 🔒 Solutions Possibles

### Solution 1: Bloquer les Attaques pour les Comptes Protégés

Ajouter une vérification dans les endpoints d'attaque:

```python
@csrf_exempt
def api_attack_full_dictionary(request):
    # ... code existant ...
    
    try:
        user = CustomUser.objects.get(username=target_username)
        
        # NOUVELLE VÉRIFICATION
        if user.protection_enabled:
            return JsonResponse({
                'error': 'Protection activée',
                'message': 'Ce compte est protégé contre les attaques automatiques.',
                'protection_enabled': True
            }, status=403)
        
        # ... reste du code ...
```

### Solution 2: Limiter le Nombre d'Attaques

Ajouter un compteur d'attaques:

```python
class CustomUser(models.Model):
    # Champs existants...
    
    # Nouveaux champs pour limiter les attaques
    attack_attempts = models.IntegerField(default=0)
    last_attack_attempt = models.DateTimeField(null=True)
    attacks_blocked_until = models.DateTimeField(null=True)
```

### Solution 3: Limiter par IP

```python
# Dans les endpoints d'attaque
ip_address = get_client_ip(request)
if is_ip_blocked(ip_address):
    return JsonResponse({
        'error': 'IP bloquée',
        'message': 'Trop d'attaques depuis cette adresse IP'
    }, status=429)
```

## 🎓 Contexte Pédagogique

Ce projet est un **TP éducatif** sur la cryptographie classique.

### Objectifs Pédagogiques
1. ✅ Comprendre les algorithmes de chiffrement classiques
2. ✅ Implémenter des techniques de cryptanalyse
3. ✅ Mesurer la sécurité des mots de passe
4. ✅ Comparer l'efficacité des protections

### Dans un Système Réel
- ❌ **Pas d'endpoints d'attaque** publics
- ✅ **Hashing des mots de passe** (bcrypt, Argon2)
- ✅ **Protection par défaut** (non opt-in)
- ✅ **Rate limiting** sur tous les endpoints
- ✅ **Blocage d'IP** après tentatives suspectes
- ✅ **CAPTCHA** après échecs
- ✅ **2FA** (authentification à deux facteurs)
- ✅ **Logging et alertes** en temps réel

## 📝 Recommandations

### Pour votre TP
1. **Expliquez la différence** entre login manuel et attaques dans votre rapport
2. **Montrez les résultats** :
   - Login avec protection → Bloque après 3 tentatives
   - Attaque avec protection → Continue normalement
3. **Discutez des limitations** du système actuel
4. **Proposez des améliorations** (voir Solutions ci-dessus)

### Si vous voulez implémenter la protection des attaques
Je peux vous aider à ajouter:
1. Vérification de protection dans les endpoints d'attaque
2. Compteur d'attaques par compte
3. Limitation par IP
4. Message informatif quand un compte protégé est attaqué

## 📊 Comparaison Visuelle

### Scénario 1: Login Manuel

```
Protection désactivée:
  Tentative 1: ❌ → Compteur: 0
  Tentative 2: ❌ → Compteur: 0
  Tentative 3: ❌ → Compteur: 0
  ...infiniment

Protection activée:
  Tentative 1: ❌ → Compteur: 1/3
  Tentative 2: ❌ → Compteur: 2/3
  Tentative 3: ❌ → Compteur: 3/3 → 🔒 BLOQUÉ 30 min
  Tentative 4: 🔒 → Refusée (compte verrouillé)
```

### Scénario 2: Attaque Automatique

```
Protection désactivée:
  Dict 1M mots: ✅ Teste tous les mots (~17 min)
  
Protection activée:
  Dict 1M mots: ✅ Teste tous les mots (~17 min)
                ⚠️  MÊME résultat !
```

## ✅ Conclusion

### État Actuel
- ✅ **Protection fonctionne** pour les logins manuels
- ❌ **Protection n'affecte PAS** les attaques automatiques
- ℹ️  C'est un choix d'architecture pour le TP éducatif

### Réponse à votre Question
**"Que se passe-t-il si j'active la protection et je lance une attaque ?"**

**Réponse:** L'attaque fonctionne **normalement**, comme si la protection n'existait pas. La protection ne bloque que les tentatives de connexion via l'endpoint `/api/login/`, pas les endpoints d'attaque pédagogiques.

### Pour Améliorer
Si vous voulez que la protection bloque aussi les attaques, vous devez:
1. Ajouter une vérification dans `api_attack_full_dictionary()`
2. Retourner une erreur 403 si `user.protection_enabled == True`
3. Documenter cette limitation/amélioration dans votre rapport

---

**Date:** 31 Octobre 2025  
**Tests:** `test_attack_protection_simple.py`  
**Résultat:** Protection n'affecte pas les attaques automatiques (par design)
