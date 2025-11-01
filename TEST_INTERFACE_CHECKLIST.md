# 🎨 TEST INTERFACE STÉGANOGRAPHIE

## ✅ Checklist de Test

### 1. Interface Générale
- [ ] Onglet "🔐 Stéganographie" visible
- [ ] Sous-onglets "📝 Texte" et "🖼️ Image" fonctionnels
- [ ] Panneau d'aide à droite visible
- [ ] Messages d'erreur/succès s'affichent correctement

---

## 📝 Tests Texte

### Test 1 : Case-Based (Cacher + Extraire)

**Étapes :**
1. Aller sur sous-onglet "📝 Texte"
2. Mode : "🔒 Cacher un message"
3. Méthode : "Case-Based"
4. Texte de couverture :
   ```
   Hello World from Paris today with beautiful weather and sunshine
   ```
5. Message secret : `HELLO`
6. Cliquer "🔒 Cacher le message"

**Résultat attendu :**
- ✅ Message de succès : "✅ Message caché avec succès ! (5 caractères)"
- ✅ Texte stéganographié affiché
- ✅ Bouton "📋 Copier" disponible

**Extraction :**
1. Passer en mode "🔓 Extraire un message"
2. Coller le texte stéganographié
3. Même méthode (Case-Based)
4. Cliquer "🔓 Extraire le message"

**Résultat attendu :**
- ✅ Message : "✅ Message extrait : "HELLO""
- ✅ Message affiché dans la boîte verte

---

### Test 2 : Analyse de Capacité

**Étapes :**
1. Texte de couverture : `The quick brown fox jumps over the lazy dog`
2. Cliquer "📊 Analyser la capacité"

**Résultat attendu :**
- ✅ Bloc d'analyse affiché
- ✅ Nombre de caractères totaux
- ✅ Nombre de lettres
- ✅ Capacité (lettres / 8)

---

### Test 3 : Erreur - Champs Vides

**Étapes :**
1. Laisser les champs vides
2. Cliquer "🔒 Cacher le message"

**Résultat attendu :**
- ✅ Message d'erreur : "Veuillez remplir tous les champs"
- ✅ Fond rouge/orange

---

## 🖼️ Tests Image

### Test 4 : Cacher un Message dans une Image

**Prérequis :** Avoir une image PNG (ex: 400×300 px)

**Étapes :**
1. Aller sur sous-onglet "🖼️ Image"
2. Mode : "🔒 Cacher un message"
3. Télécharger une image
4. Message secret : `This is a secret message hidden in the image!`
5. Cliquer "🔒 Cacher dans l'image"

**Résultat attendu :**
- ✅ Analyse automatique de l'image (dimensions, capacité)
- ✅ Pourcentage d'utilisation affiché
- ✅ Message de succès avec stats
- ✅ Image stéganographiée affichée
- ✅ Bouton "💾 Télécharger l'image"

---

### Test 5 : Extraire d'une Image

**Étapes :**
1. Passer en mode "🔓 Extraire un message"
2. Télécharger l'image stéganographiée du test précédent
3. Cliquer "🔓 Extraire le message"

**Résultat attendu :**
- ✅ Message de succès avec nombre de caractères
- ✅ Message extrait affiché dans la boîte verte
- ✅ Message identique à celui caché

---

### Test 6 : Erreur - Pas d'Image

**Étapes :**
1. Ne pas télécharger d'image
2. Cliquer "🔒 Cacher dans l'image"

**Résultat attendu :**
- ✅ Message d'erreur : "Veuillez sélectionner une image et entrer un message"

---

## 🔄 Tests de Bout en Bout

### Scénario Complet : Texte

```
1. Cacher "SECRET" dans "Hello World..."
2. Copier le résultat
3. Passer en mode extraction
4. Coller le texte
5. Extraire
6. Vérifier que "SECRET" est retrouvé
```

**Résultat :** ✅ / ❌

---

### Scénario Complet : Image

```
1. Créer image via API (optionnel)
2. Télécharger image locale
3. Cacher message long (100+ caractères)
4. Télécharger l'image stéganographiée
5. Extraire depuis la même image
6. Vérifier message identique
```

**Résultat :** ✅ / ❌

---

## 🎨 Tests Visuels

### Interface
- [ ] Police lisible
- [ ] Boutons bien alignés
- [ ] Couleurs cohérentes avec le reste de l'app
- [ ] Responsive (s'adapte à la taille d'écran)

### Messages
- [ ] Succès en vert
- [ ] Erreurs en rouge
- [ ] Icônes appropriés (🔒, 🔓, ✅, ⚠️)

### Images
- [ ] Preview correcte
- [ ] Taille adaptée (max 300px height)
- [ ] Bordure visible
- [ ] Image stéganographiée identique visuellement

---

## 🚀 Tests de Performance

### Temps de Réponse Acceptable

| Operation | Temps attendu |
|-----------|--------------|
| Cacher texte | < 1 seconde |
| Extraire texte | < 1 seconde |
| Cacher image (400×300) | < 2 secondes |
| Extraire image | < 2 secondes |
| Analyser capacité | < 500ms |

---

## 🔧 Tests Techniques

### API Endpoints Utilisés

```javascript
POST /api/stego/text/hide/
POST /api/stego/text/extract/
POST /api/stego/image/hide/
POST /api/stego/image/extract/
POST /api/stego/analyze/text/
POST /api/stego/analyze/image/
```

**Test Console** : Ouvrir DevTools → Network → Vérifier les appels

---

## 📊 Résultats des Tests

### Texte
- [ ] Test 1 : Case-Based ✅ / ❌
- [ ] Test 2 : Analyse capacité ✅ / ❌
- [ ] Test 3 : Erreur champs vides ✅ / ❌

### Image
- [ ] Test 4 : Cacher message ✅ / ❌
- [ ] Test 5 : Extraire message ✅ / ❌
- [ ] Test 6 : Erreur pas d'image ✅ / ❌

### Bout en Bout
- [ ] Scénario texte complet ✅ / ❌
- [ ] Scénario image complet ✅ / ❌

### Interface
- [ ] Visuellement cohérent ✅ / ❌
- [ ] Responsive ✅ / ❌
- [ ] Performances acceptables ✅ / ❌

---

## 🐛 Bugs Connus

### Backend (à corriger)
1. **Whitespace extraction** : Retourne chaîne vide
2. **Zerowidth extraction** : Message partiel
3. **LSB delimiter** : Artifacts dans extraction ("<<<EN")

### Frontend (état actuel)
- ✅ Aucun bug connu
- ⚠️ Dépend du backend pour fonctionner

---

## 📝 Notes de Test

**Date du test :** _____________________

**Testeur :** _____________________

**Environnement :**
- OS : Windows
- Navigateur : _____________________
- Frontend : http://localhost:3001/
- Backend : http://localhost:8000/

**Commentaires généraux :**
```
_______________________________________________
_______________________________________________
_______________________________________________
```

**Bugs trouvés :**
```
_______________________________________________
_______________________________________________
_______________________________________________
```

**Améliorations suggérées :**
```
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## ✅ Validation Finale

**L'interface stéganographie est-elle prête pour la démonstration ?**

- [ ] Oui, tous les tests passent ✅
- [ ] Oui, avec quelques bugs mineurs ⚠️
- [ ] Non, nécessite des corrections ❌

**Recommandations :**
```
_______________________________________________
_______________________________________________
```
