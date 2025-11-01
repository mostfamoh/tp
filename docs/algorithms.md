# Documentation des Algorithmes de Chiffrement Classique
**TP SSAD - USTHB - Professeur H. Nacer - Octobre 2025**

---

## Table des matières
1. [Chiffrement de César](#1-chiffrement-de-césar)
2. [Chiffrement Affine](#2-chiffrement-affine)
3. [Chiffrement Playfair](#3-chiffrement-playfair)
4. [Chiffrement de Hill](#4-chiffrement-de-hill)
5. [Comparaison et Analyse de Sécurité](#5-comparaison-et-analyse-de-sécurité)

---

## 1. Chiffrement de César

### 1.1 Description
Le chiffrement de César est l'un des plus anciens systèmes de chiffrement par substitution. Chaque lettre du texte clair est remplacée par une lettre située à *n* positions plus loin dans l'alphabet.

### 1.2 Formulation mathématique

**Chiffrement:**
```
E(x) = (x + k) mod 26
```

**Déchiffrement:**
```
D(y) = (y - k) mod 26
```

Où:
- `x` = position de la lettre en clair (A=0, B=1, ..., Z=25)
- `y` = position de la lettre chiffrée
- `k` = clé de décalage (0 ≤ k ≤ 25)
- `mod 26` = opération modulo 26 (nombre de lettres de l'alphabet)

### 1.3 Exemple de calcul

**Texte clair:** HELLO  
**Clé:** k = 3

| Lettre | Position x | Calcul | Position y | Lettre chiffrée |
|--------|-----------|---------|-----------|-----------------|
| H      | 7         | (7+3) mod 26 = 10 | 10 | K |
| E      | 4         | (4+3) mod 26 = 7  | 7  | H |
| L      | 11        | (11+3) mod 26 = 14 | 14 | O |
| L      | 11        | (11+3) mod 26 = 14 | 14 | O |
| O      | 14        | (14+3) mod 26 = 17 | 17 | R |

**Résultat:** HELLO → KHOOR

### 1.4 Avantages
- ✅ Très simple à implémenter
- ✅ Rapide à calculer
- ✅ Facile à comprendre et à enseigner
- ✅ Historiquement important (utilisé par Jules César)

### 1.5 Failles de sécurité
- ❌ **Espace de clés très petit:** Seulement 25 clés possibles (k=0 est trivial)
- ❌ **Vulnérable aux attaques par force brute:** Un ordinateur peut tester toutes les clés en quelques millisecondes
- ❌ **Vulnérable à l'analyse de fréquence:** Les lettres fréquentes (E, A, S en français) restent fréquentes après chiffrement
- ❌ **Pas de diffusion:** Chaque lettre est chiffrée indépendamment
- ❌ **Préservation des motifs:** Les mots répétés restent répétés dans le texte chiffré

### 1.6 Attaques possibles
1. **Force brute:** Tester les 25 clés possibles
2. **Analyse de fréquence:** Identifier la lettre la plus fréquente et supposer qu'elle correspond à 'E'
3. **Attaque par mot connu:** Si on connaît un mot du texte clair, on peut déduire la clé

---

## 2. Chiffrement Affine

### 2.1 Description
Le chiffrement affine est une généralisation du chiffrement de César. Il utilise une fonction affine pour transformer chaque lettre : multiplication suivie d'une addition, le tout modulo 26.

### 2.2 Formulation mathématique

**Chiffrement:**
```
E(x) = (a × x + b) mod 26
```

**Déchiffrement:**
```
D(y) = a⁻¹ × (y - b) mod 26
```

Où:
- `x` = position de la lettre en clair (A=0, B=1, ..., Z=25)
- `y` = position de la lettre chiffrée
- `a` = coefficient multiplicatif (doit être copremier avec 26)
- `b` = décalage additif (0 ≤ b ≤ 25)
- `a⁻¹` = inverse modulaire de `a` modulo 26

**Valeurs valides pour a:**
```
a ∈ {1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25}
```
Ce sont les 12 nombres copremiers avec 26 (φ(26) = 12).

### 2.3 Calcul de l'inverse modulaire

Pour déchiffrer, on doit trouver `a⁻¹` tel que:
```
a × a⁻¹ ≡ 1 (mod 26)
```

**Table des inverses modulaires:**

| a  | a⁻¹ |
|----|-----|
| 1  | 1   |
| 3  | 9   |
| 5  | 21  |
| 7  | 15  |
| 9  | 3   |
| 11 | 19  |
| 15 | 7   |
| 17 | 23  |
| 19 | 11  |
| 21 | 5   |
| 23 | 17  |
| 25 | 25  |

### 2.4 Exemple de calcul

**Texte clair:** HELLO  
**Clés:** a = 5, b = 8

| Lettre | x  | Calcul | y | Lettre chiffrée |
|--------|-------|---------|-------|-----------------|
| H      | 7     | (5×7+8) mod 26 = 43 mod 26 = 17 | 17 | R |
| E      | 4     | (5×4+8) mod 26 = 28 mod 26 = 2  | 2  | C |
| L      | 11    | (5×11+8) mod 26 = 63 mod 26 = 11 | 11 | L |
| L      | 11    | (5×11+8) mod 26 = 63 mod 26 = 11 | 11 | L |
| O      | 14    | (5×14+8) mod 26 = 78 mod 26 = 0  | 0  | A |

**Résultat:** HELLO → RCLLA

**Déchiffrement de R:**
- a⁻¹ = 21 (inverse de 5 mod 26)
- y = 17 (position de R)
- x = 21 × (17 - 8) mod 26 = 21 × 9 mod 26 = 189 mod 26 = 7 → H ✓

### 2.5 Avantages
- ✅ Plus sécurisé que César (312 clés possibles au lieu de 25)
- ✅ Simple à implémenter
- ✅ Rapide à calculer
- ✅ Introduction aux concepts de l'arithmétique modulaire

### 2.6 Failles de sécurité
- ❌ **Espace de clés limité:** Seulement 12 × 26 = 312 combinaisons possibles
- ❌ **Vulnérable à la force brute:** Un ordinateur moderne peut tester toutes les clés en moins d'une seconde
- ❌ **Vulnérable à l'analyse de fréquence:** Comme César, les fréquences des lettres sont préservées
- ❌ **Attaque par texte clair connu:** Avec seulement 2 lettres connues, on peut résoudre le système d'équations pour trouver a et b
- ❌ **Chiffrement monoalphabétique:** Chaque lettre est toujours chiffrée de la même façon

### 2.7 Attaque par texte clair connu

Si on connaît deux paires (x₁, y₁) et (x₂, y₂):
```
y₁ = ax₁ + b (mod 26)
y₂ = ax₂ + b (mod 26)
```

On peut résoudre:
```
y₁ - y₂ = a(x₁ - x₂) (mod 26)
a = (y₁ - y₂) × (x₁ - x₂)⁻¹ (mod 26)
b = y₁ - ax₁ (mod 26)
```

---

## 3. Chiffrement Playfair

### 3.1 Description
Le chiffrement Playfair, inventé en 1854 par Charles Wheatstone, est le premier chiffrement par substitution de **digrammes** (paires de lettres). Il utilise une matrice 5×5 construite à partir d'un mot-clé.

### 3.2 Construction de la matrice

1. Écrire le mot-clé (sans répétition de lettres)
2. Compléter avec les lettres restantes de l'alphabet
3. Fusionner I et J (règle classique)

**Exemple avec le mot-clé "MONARCHY":**

```
M O N A R
C H Y B D
E F G I K
L P Q S T
U V W X Z
```

### 3.3 Règles de chiffrement

Pour chaque paire de lettres (digramme):

1. **Si les deux lettres sont identiques:**  
   Insérer un 'X' entre elles
   - Exemple: HELLO → HE LX LO

2. **Si les lettres sont sur la même ligne:**  
   Remplacer chacune par la lettre immédiatement à droite (avec retour circulaire)
   - AR → RM (dans la ligne MONAR)

3. **Si les lettres sont dans la même colonne:**  
   Remplacer chacune par la lettre immédiatement en dessous (avec retour circulaire)

4. **Si les lettres forment un rectangle:**  
   Remplacer chaque lettre par celle située sur la même ligne mais dans la colonne de l'autre lettre
   - HE → GD

### 3.4 Exemple complet

**Texte clair:** HELLO  
**Mot-clé:** MONARCHY  
**Matrice:** (voir ci-dessus)

**Préparation:** HELLO → HE LX LO

| Paire | Règle | Résultat |
|-------|-------|----------|
| HE    | Rectangle | GD |
| LX    | Rectangle | RW |
| LO    | Rectangle | PM |

**Résultat:** HELLO → GDRWPM

### 3.5 Avantages
- ✅ **Chiffrement de digrammes:** Masque partiellement les fréquences des lettres
- ✅ **Espace de clés plus grand:** 25! / (25-k)! possibilités (k = longueur du mot-clé)
- ✅ **Résistant à l'analyse de fréquence simple:** Les fréquences des lettres individuelles sont brouillées
- ✅ **Historiquement robuste:** Utilisé jusqu'à la Première Guerre mondiale
- ✅ **Pas besoin d'ordinateur pour chiffrer/déchiffrer**

### 3.6 Failles de sécurité
- ❌ **Vulnérable à l'analyse de fréquence des digrammes:** En français/anglais, certaines paires (TH, ER, ON) sont très fréquentes
- ❌ **Motifs préservés:** Les digrammes répétés restent répétés
- ❌ **Fusion I/J:** Perte d'information (ambiguïté au déchiffrement)
- ❌ **Attaque par mot connu:** Si on connaît plusieurs mots du texte clair, on peut reconstruire la matrice
- ❌ **Longueur du texte chiffré:** Toujours paire (ajout de 'X' révèle la structure)

### 3.7 Cryptanalyse moderne
- Analyse de fréquence des digrammes
- Attaque par force brute sur le mot-clé (si limité à un dictionnaire)
- Algorithmes génétiques pour optimiser la matrice

---

## 4. Chiffrement de Hill

### 4.1 Description
Le chiffrement de Hill, inventé en 1929 par Lester S. Hill, est le premier chiffrement polygraphique basé sur l'**algèbre linéaire**. Il utilise des multiplications matricielles modulo 26.

### 4.2 Formulation mathématique (matrice 2×2)

**Matrice clé:**
```
K = | a  b |
    | c  d |
```

**Chiffrement:**
```
C = K × P (mod 26)
```

**Déchiffrement:**
```
P = K⁻¹ × C (mod 26)
```

Où:
- P = vecteur du texte clair (paires de lettres converties en nombres)
- C = vecteur du texte chiffré
- K⁻¹ = inverse modulaire de K

### 4.3 Condition d'inversibilité

Pour que la matrice K soit inversible modulo 26:
```
gcd(det(K), 26) = 1
```

Où `det(K) = ad - bc` (déterminant de K)

**Calcul de l'inverse modulaire:**
```
K⁻¹ = det(K)⁻¹ × adj(K) (mod 26)
```

Pour une matrice 2×2:
```
adj(K) = |  d  -b |
         | -c   a |
```

### 4.4 Exemple de calcul (2×2)

**Texte clair:** HELP  
**Matrice clé:**
```
K = | 3  3 |
    | 2  5 |
```

**Vérification d'inversibilité:**
- det(K) = 3×5 - 3×2 = 15 - 6 = 9
- gcd(9, 26) = 1 ✓ (inversible)
- 9⁻¹ mod 26 = 3 (car 9 × 3 = 27 ≡ 1 mod 26)

**Chiffrement du premier digramme "HE":**
```
P = | H |   | 7  |
    | E | = | 4  |

C = K × P = | 3  3 | × | 7 | = | 33 | = | 7  | (mod 26)
            | 2  5 |   | 4 |   | 34 |   | 8  |

C = | H |
    | I |
```

**Chiffrement du deuxième digramme "LP":**
```
P = | 11 |
    | 15 |

C = | 3  3 | × | 11 | = | 78  | = | 0  | (mod 26)
    | 2  5 |   | 15 |   | 97  |   | 19 |

C = | A |
    | T |
```

**Résultat:** HELP → HIAT

### 4.5 Exemple 3×3

Pour une matrice 3×3, on chiffre des trigrammes (groupes de 3 lettres):

**Matrice clé:**
```
K = | 6   24   1 |
    | 13  16  10 |
    | 20  17  15 |
```

**Texte clair:** ACT  
```
P = | 0  |
    | 2  |
    | 19 |

C = K × P (mod 26) = | 67  | = | 15 | → P
                     | 232 |   | 24 |   Y
                     | 375 |   | 11 |   L
```

**Résultat:** ACT → PYL

### 4.6 Avantages
- ✅ **Très sécurisé pour son époque:** Basé sur les mathématiques modernes
- ✅ **Masque complètement les fréquences:** Chaque lettre dépend de plusieurs lettres du texte clair
- ✅ **Diffusion excellente:** Une lettre du texte clair affecte plusieurs lettres du texte chiffré
- ✅ **Espace de clés énorme:** Pour une matrice 3×3, environ 26⁹ ≈ 5,4 × 10¹² possibilités
- ✅ **Base théorique solide:** Utilise l'algèbre linéaire rigoureuse

### 4.7 Failles de sécurité
- ❌ **Vulnérable à l'attaque par texte clair connu:**  
  Si on connaît n paires (texte clair, texte chiffré) où n = taille de la matrice, on peut résoudre un système d'équations linéaires pour trouver K
  
- ❌ **Complexité de calcul:** Pour grandes matrices, le chiffrement/déchiffrement devient lent sans optimisation

- ❌ **Choix de la clé critique:** Beaucoup de matrices ne sont pas inversibles modulo 26

- ❌ **Pas de diffusion inter-blocs:** Chaque bloc est chiffré indépendamment (mode ECB), donc les blocs répétés restent répétés

### 4.8 Attaque par texte clair connu (2×2)

Si on connaît 2 digrammes et leurs versions chiffrées:
```
C₁ = K × P₁
C₂ = K × P₂
```

On peut écrire:
```
[C₁ C₂] = K × [P₁ P₂]
```

Si [P₁ P₂] est inversible:
```
K = [C₁ C₂] × [P₁ P₂]⁻¹ (mod 26)
```

**Exemple:**
- Texte clair connu: "HELP" → HE, LP
- Texte chiffré: "HIAT" → HI, AT

```
P_matrix = | 7  11 |     C_matrix = | 7  0  |
           | 4  15 |                 | 8  19 |
```

On peut résoudre pour trouver K.

---

## 5. Comparaison et Analyse de Sécurité

### 5.1 Tableau comparatif

| Critère | César | Affine | Playfair | Hill (2×2) |
|---------|-------|--------|----------|------------|
| **Espace de clés** | 25 | 312 | ≈ 10²⁶ | ≈ 67,000 |
| **Taille du bloc** | 1 lettre | 1 lettre | 2 lettres | 2 lettres |
| **Vitesse** | Très rapide | Très rapide | Rapide | Moyen |
| **Résistance force brute** | Nulle | Très faible | Moyenne | Faible |
| **Résistance fréquence** | Nulle | Nulle | Moyenne | Élevée |
| **Complexité implémentation** | Triviale | Simple | Moyenne | Élevée |
| **Diffusion** | Nulle | Nulle | Faible | Élevée |
| **Historique** | Antiquité | 1800s | 1854 | 1929 |

### 5.2 Temps de cassage (estimations)

Sur un ordinateur moderne (10⁹ opérations/seconde):

| Algorithme | Force brute | Analyse fréquence |
|------------|-------------|-------------------|
| César      | < 1 ms      | < 1 seconde       |
| Affine     | < 1 ms      | < 1 seconde       |
| Playfair   | Infaisable* | Minutes-Heures    |
| Hill (2×2) | Minutes     | N/A (résistant)   |

*Avec mot-clé limité: heures-jours

### 5.3 Recommandations pour le TP

**Pour l'apprentissage:**
1. **César:** Excellent pour comprendre les bases du chiffrement
2. **Affine:** Introduction à l'arithmétique modulaire
3. **Playfair:** Complexité intermédiaire, bon équilibre
4. **Hill:** Concepts avancés d'algèbre linéaire

**Pour la sécurité réelle:**
- ❌ **Aucun de ces algorithmes n'est sécurisé pour un usage moderne**
- ✅ Utiliser AES, RSA, ou autres algorithmes modernes certifiés
- ✅ Ces algorithmes classiques sont **uniquement pédagogiques**

### 5.4 Vulnérabilités communes

Tous ces algorithmes souffrent de:
1. **Pas de confusion moderne:** Structure trop simple
2. **Pas de diffusion inter-blocs:** Mode ECB implicite
3. **Pas de sel/IV:** Textes identiques → chiffrés identiques
4. **Pas d'authentification:** Vulnérables aux modifications
5. **Clés statiques:** Pas de gestion de clés moderne

### 5.5 Leçons pour la cryptographie moderne

Ces algorithmes classiques enseignent:
- ✅ **Importance de l'espace de clés:** Plus grand = plus sécurisé
- ✅ **Confusion et diffusion:** Principes de Shannon (1949)
- ✅ **Analyse de fréquence:** Toujours une menace
- ✅ **Mathématiques rigoureuses:** Base de la cryptographie moderne
- ✅ **Tests et validation:** Nécessité de prouver la sécurité

---

## 6. Conclusion

Les algorithmes de chiffrement classique présentés (César, Affine, Playfair, Hill) sont des jalons historiques importants dans l'évolution de la cryptographie. Bien qu'obsolètes pour un usage sécurisé moderne, ils illustrent des concepts fondamentaux:

- **Substitution** (César, Affine)
- **Transposition** (partiellement dans Playfair)
- **Algèbre linéaire** (Hill)
- **Confusion et diffusion** (Hill)

Ces concepts sont repris et améliorés dans les algorithmes modernes comme AES (Advanced Encryption Standard), qui combine:
- Substitutions non-linéaires (S-boxes)
- Permutations (ShiftRows, MixColumns)
- Mathématiques avancées (corps de Galois GF(2⁸))
- Multiples tours (10-14 tours pour AES)

**Pour ce TP:** Ces algorithmes permettent de comprendre les mécanismes de base, d'implémenter des attaques simples, et d'apprécier la complexité de la cryptographie moderne.

---

**Références:**
- Stinson, D. R. (2005). *Cryptography: Theory and Practice*
- Menezes, A. J., et al. (1996). *Handbook of Applied Cryptography*
- Schneier, B. (1996). *Applied Cryptography*
- NIST FIPS 197 (AES Standard)
