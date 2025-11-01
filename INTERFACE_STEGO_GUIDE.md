# 🎨 Interface Stéganographie - Guide d'Utilisation

## 🚀 Accès Rapide

**URL de l'application :** `http://localhost:3001/`

**Onglet Stéganographie :** 🔐 Stéganographie (5ème onglet)

---

## 📝 Stéganographie Texte

### Mode "Cacher un message"

1. **Choisir la méthode** :
   - ✅ **Case-Based** (Recommandé) - Utilise la casse des lettres
   - WhiteSpace - Utilise espaces et tabulations
   - Zero-Width - Utilise caractères Unicode invisibles

2. **Entrer le texte de couverture** :
   ```
   Exemple : "La cryptographie est une science fascinante qui protege les donnees"
   ```
   - Cliquez sur "📊 Analyser la capacité" pour voir combien de caractères peuvent être cachés

3. **Entrer le message secret** :
   ```
   Exemple : "HELLO"
   ```

4. **Cliquer sur "🔒 Cacher le message"**

5. **Résultat** :
   - Le texte stéganographié s'affiche
   - Copiez-le avec le bouton "📋 Copier"
   - Exemple de résultat : "La CrYptoGrapHie Est..."

### Mode "Extraire un message"

1. **Passer en mode extraction**
2. **Coller le texte stéganographié**
3. **Choisir la même méthode** utilisée pour cacher
4. **Cliquer sur "🔓 Extraire le message"**
5. **Le message secret s'affiche** : "HELLO"

---

## 🖼️ Stéganographie Image

### Mode "Cacher un message"

1. **Télécharger une image** :
   - Formats supportés : PNG, JPG, BMP
   - Taille recommandée : 400×300 ou plus
   - L'analyse de capacité s'affiche automatiquement

2. **Entrer le message secret** :
   ```
   Exemple : "This is a top secret message hidden in this image!"
   ```
   - Le pourcentage d'utilisation s'affiche en temps réel

3. **Cliquer sur "🔒 Cacher dans l'image"**

4. **Télécharger l'image stéganographiée** :
   - Cliquez sur "💾 Télécharger l'image"
   - L'image est **visuellement identique** à l'originale !

### Mode "Extraire un message"

1. **Passer en mode extraction**
2. **Télécharger l'image stéganographiée**
3. **Cliquer sur "🔓 Extraire le message"**
4. **Le message secret s'affiche**

---

## 📊 Exemple Complet - Texte

### Étape 1 : Cacher
```
Texte de couverture : "Bonjour tout le monde, la cryptographie est passionnante"
Message secret : "HI"
Méthode : Case-Based
```

### Étape 2 : Résultat
```
Texte stéganographié : "BOnjour tout Le monde, la CryPtogrAphie est paSsionnante"
                          ^^            ^            ^^  ^   ^       ^^
                          H             I (en binaire)
```

### Étape 3 : Extraire
```
Coller le texte stéganographié
→ Message extrait : "HI"
```

---

## 🖼️ Exemple Complet - Image

### Scénario : Envoyer un message secret à un collègue

1. **Préparer** :
   - Photo de paysage (400×300 px)
   - Message : "Rendez-vous demain 14h bureau 305"

2. **Cacher** :
   - Télécharger la photo
   - Entrer le message
   - Télécharger l'image stéganographiée

3. **Envoyer** :
   - Envoyer l'image par email/chat
   - **Personne ne verra de différence !**

4. **Recevoir** :
   - Collègue télécharge l'image
   - Utilise l'outil pour extraire
   - Reçoit le message secret !

---

## 📈 Capacités

### Texte (Case-Based)
| Lettres dans le texte | Caractères cachables |
|----------------------|---------------------|
| 80 lettres           | 10 caractères       |
| 160 lettres          | 20 caractères       |
| 320 lettres          | 40 caractères       |

**Formule** : `Capacité = Nombre de lettres / 8`

### Image (LSB)
| Dimensions | Pixels totaux | Capacité max | Recommandé (50%) |
|-----------|--------------|-------------|-----------------|
| 400×300   | 120,000      | 45,000 chars | 22,500 chars   |
| 800×600   | 480,000      | 180,000 chars | 90,000 chars  |
| 1920×1080 | 2,073,600    | 777,600 chars | 388,800 chars |

**Formule** : `Capacité = (Largeur × Hauteur × 3) / 8`

---

## 💡 Astuces

### ✅ Bonnes Pratiques

1. **Texte** :
   - Utilisez Case-Based (la plus fiable)
   - Analysez la capacité avant de cacher
   - Gardez le texte naturel et non suspect

2. **Image** :
   - Utilisez des formats non compressés (PNG)
   - Ne dépassez pas 50% de la capacité
   - Évitez les images trop petites

3. **Sécurité** :
   - Combinez avec la cryptographie (chiffrer puis cacher)
   - Ne réutilisez pas la même image plusieurs fois
   - Partagez la méthode utilisée de manière sécurisée

### ⚠️ À Éviter

1. **Texte** :
   - ❌ WhiteSpace/Zero-Width sur des plateformes qui nettoient le texte
   - ❌ Messages trop longs pour la capacité
   - ❌ Texte de couverture trop court

2. **Image** :
   - ❌ JPEG (compression lossy détruit le message)
   - ❌ Utiliser 100% de la capacité (détectable)
   - ❌ Images avec très peu de variations de couleurs

---

## 🔬 Tests et Démonstrations

### Test Rapide - Texte

1. Allez sur l'onglet 🔐 Stéganographie
2. Sous-onglet "📝 Texte"
3. Texte : `"Hello World from Paris today with beautiful weather"`
4. Message : `"HI"`
5. Méthode : Case-Based
6. Cliquez "🔒 Cacher"
7. Résultat : `"HEllo WorLd..."`
8. Passez en mode "Extraire"
9. Collez le résultat
10. Cliquez "🔓 Extraire"
11. ✅ Vous verrez : `"HI"`

### Test Rapide - Image

1. Téléchargez une image quelconque (PNG recommandé)
2. Message : `"Secret test message"`
3. Cliquez "🔒 Cacher dans l'image"
4. Téléchargez l'image stéganographiée
5. Passez en mode "Extraire"
6. Téléchargez l'image stéganographiée
7. Cliquez "🔓 Extraire"
8. ✅ Vous verrez : `"Secret test message"`

---

## 🎓 Explication Technique

### Case-Based (Texte)

**Principe** : Utilise la casse (majuscule/minuscule) des lettres pour encoder un bit :
- Majuscule = `1`
- Minuscule = `0`

**Exemple** : Pour cacher "H" (ASCII 72 = `01001000` en binaire)
```
Texte original : "bonjour tout le monde"
Après codage :   "bOnjoUr toUt lE monde"
                  0 1  0  0  1  0 (= H)
```

### LSB Image

**Principe** : Modifie le **bit de poids faible** (Least Significant Bit) de chaque composante RGB :
- Pixel RGB(145, 67, 200) → RGB(145, 66, 201)
- Différence invisible à l'œil nu !

**Structure du message** :
1. 32 premiers bits = longueur du message
2. Bits suivants = message en binaire
3. Délimiteur `<<<END>>>` pour marquer la fin

---

## 📚 Pour Aller Plus Loin

### Combinaison Crypto + Stégo

1. **Chiffrer** le message (onglet Inscription/Connexion)
   - Message : `"SECRET"`
   - Algorithme : César avec clé 3
   - Résultat chiffré : `"VHFUHW"`

2. **Cacher** le message chiffré (onglet Stéganographie)
   - Message : `"VHFUHW"`
   - Image ou texte de couverture
   - Résultat : Message doublement protégé !

3. **Avantage** :
   - Même si quelqu'un détecte la stéganographie
   - Il ne verra qu'un message chiffré
   - Double couche de sécurité !

---

## 🆘 Dépannage

### "Extraction retourne un message vide"

**Causes possibles** :
- ✅ Vérifiez que vous utilisez la **même méthode** pour cacher et extraire
- ✅ Pour les images, assurez-vous que l'image n'a pas été compressée (évitez JPEG)
- ✅ Pour le texte, vérifiez que le texte n'a pas été modifié (copié/collé)

### "Capacité insuffisante"

**Solutions** :
- Utilisez un texte/image plus grand
- Réduisez la taille du message secret
- Pour le texte : méthode Case-Based nécessite 8 lettres par caractère caché

### "Image téléchargée différente de l'originale"

**Normal !** :
- Les pixels sont **légèrement modifiés**
- Différence invisible à l'œil nu
- Comparez avec un outil d'analyse d'image pour voir les modifications

---

## 🎯 Objectifs Pédagogiques

Ce module de stéganographie permet de comprendre :

1. **La différence entre cryptographie et stéganographie**
2. **Comment cacher des données sans éveiller les soupçons**
3. **Les limites de la stéganographie** (détection, capacité)
4. **L'importance de la combinaison crypto + stégo**

---

**Prêt à cacher vos premiers messages secrets ? 🕵️‍♂️**

**Accédez à l'interface :** `http://localhost:3001/` → Onglet "🔐 Stéganographie"
