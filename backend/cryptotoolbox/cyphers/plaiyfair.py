"""
Chiffrement Playfair - TP SSAD USTHB
Chiffrement par substitution utilisant une matrice 5x5
Règle classique: I et J sont fusionnés
"""
import numpy as np


def clean_text(s: str) -> str:
    """Nettoie le texte: minuscules uniquement, supprime espaces et ponctuation."""
    return ''.join(ch for ch in s.lower() if ch.isalpha())


def generate_matrix(keyword: str):
    """
    Génère la matrice 5x5 de Playfair à partir d'un mot-clé.
    
    Args:
        keyword (str): Mot-clé pour générer la matrice
    
    Returns:
        np.array: Matrice 5x5
    """
    keyword = clean_text(keyword)
    final_keyword = ""
    for letter in keyword:
        if letter not in final_keyword:
            final_keyword += letter

    matrix = [letter for letter in final_keyword]
    alphabet = [chr(i) for i in range(97, 123)]
    for letter in alphabet:
        if letter == 'j':  # règle classique Playfair
            continue
        elif letter not in matrix:
            matrix.append(letter)
    return np.array(matrix).reshape(5, 5)


def prepare_plaintext(plaintext: str):
    """
    Prépare le texte en clair pour Playfair (paires de lettres).
    
    Args:
        plaintext (str): Texte en clair
    
    Returns:
        list: Liste de paires de caractères
    """
    plaintext = clean_text(plaintext).replace('j', 'i')
    plaintext_pair = []
    i = 0
    while i < len(plaintext):
        if i == len(plaintext) - 1:
            plaintext_pair.append(plaintext[i] + 'x')
            i += 1
        elif plaintext[i] == plaintext[i + 1]:
            plaintext_pair.append(plaintext[i] + 'x')
            i += 1
        else:
            plaintext_pair.append(plaintext[i] + plaintext[i + 1])
            i += 2
    return plaintext_pair


def encrypt_playfair(keyword: str, plaintext: str):
    """
    Chiffre un texte avec Playfair.
    
    Args:
        keyword (str): Mot-clé pour générer la matrice
        plaintext (str): Texte en clair
    
    Returns:
        str: Texte chiffré
    
    Exemple:
        >>> encrypt_playfair("MONARCHY", "HELLO")
        'DMYRANVO'
    """
    matrix = generate_matrix(keyword)
    plaintext_pair = prepare_plaintext(plaintext)
    textchiffre = ""

    for pair in plaintext_pair:
        pair_man = False
        # Même ligne
        for row in range(5):
            row_current = matrix[row, :]
            if pair[0] in row_current and pair[1] in row_current:
                first_letter = list(row_current).index(pair[0])
                second_letter = list(row_current).index(pair[1])
                textchiffre += matrix[row, (first_letter + 1) % 5]
                textchiffre += matrix[row, (second_letter + 1) % 5]
                pair_man = True
                break

        if pair_man:
            continue

        # Même colonne
        for col in range(5):
            col_current = matrix[:, col]
            if pair[0] in col_current and pair[1] in col_current:
                first_letter = list(col_current).index(pair[0])
                second_letter = list(col_current).index(pair[1])
                textchiffre += matrix[(first_letter + 1) % 5, col]
                textchiffre += matrix[(second_letter + 1) % 5, col]
                pair_man = True
                break

        if pair_man:
            continue

        # Rectangle
        first_letter_cor = np.where(matrix == pair[0])
        second_letter_cor = np.where(matrix == pair[1])
        textchiffre += matrix[first_letter_cor[0][0], second_letter_cor[1][0]]
        textchiffre += matrix[second_letter_cor[0][0], first_letter_cor[1][0]]

    return textchiffre.upper()


def decrypt_playfair(keyword: str, ciphertext: str):
    """
    Déchiffre un texte chiffré avec Playfair.
    
    Args:
        keyword (str): Mot-clé utilisé pour le chiffrement
        ciphertext (str): Texte chiffré
    
    Returns:
        str: Texte en clair
    """
    matrix = generate_matrix(keyword)
    ciphertext = clean_text(ciphertext).replace('j', 'i')
    pairs = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    textchiffre = ""

    for pair in pairs:
        pair_man = False
        # Même ligne
        for row in range(5):
            row_current = matrix[row, :]
            if pair[0] in row_current and pair[1] in row_current:
                first_letter = list(row_current).index(pair[0])
                second_letter = list(row_current).index(pair[1])
                textchiffre += matrix[row, (first_letter - 1) % 5]
                textchiffre += matrix[row, (second_letter - 1) % 5]
                pair_man = True
                break

        if pair_man:
            continue

        # Même colonne
        for col in range(5):
            col_current = matrix[:, col]
            if pair[0] in col_current and pair[1] in col_current:
                first_letter = list(col_current).index(pair[0])
                second_letter = list(col_current).index(pair[1])
                textchiffre += matrix[(first_letter - 1) % 5, col]
                textchiffre += matrix[(second_letter - 1) % 5, col]
                pair_man = True
                break

        if pair_man:
            continue

        # Rectangle
        first_letter_cor = np.where(matrix == pair[0])
        second_letter_cor = np.where(matrix == pair[1])
        textchiffre += matrix[first_letter_cor[0][0], second_letter_cor[1][0]]
        textchiffre += matrix[second_letter_cor[0][0], first_letter_cor[1][0]]

    # Nettoyer les 'x' de remplissage
    i = 0
    text = ""
    while i < len(textchiffre):
        if i > 0 and i < len(textchiffre) - 1 and textchiffre[i] == 'x' and textchiffre[i-1] == textchiffre[i+1]:
            i += 1
        elif i == len(textchiffre) - 1 and textchiffre[i] == 'x':
            i += 1
        else:
            text += textchiffre[i]
            i += 1
    return text.upper()


def explain_steps(keyword: str, plaintext: str) -> dict:
    """
    Explique les étapes du chiffrement Playfair (pour documentation/rapport).
    
    Args:
        keyword (str): Mot-clé
        plaintext (str): Texte à chiffrer
    
    Returns:
        dict: Détails du chiffrement étape par étape
    """
    matrix = generate_matrix(keyword)
    pairs = prepare_plaintext(plaintext)
    
    steps = {
        "algorithm": "Playfair",
        "keyword": keyword.upper(),
        "plaintext": clean_text(plaintext).upper(),
        "matrix": matrix.tolist(),
        "pairs": [p.upper() for p in pairs],
        "steps": [],
        "ciphertext": ""
    }
    
    cipher = ""
    for pair in pairs:
        pair_result = {"pair": pair.upper(), "rule": "", "result": ""}
        
        # Vérifier même ligne
        for row in range(5):
            row_current = matrix[row, :]
            if pair[0] in row_current and pair[1] in row_current:
                first_letter = list(row_current).index(pair[0])
                second_letter = list(row_current).index(pair[1])
                c1 = matrix[row, (first_letter + 1) % 5]
                c2 = matrix[row, (second_letter + 1) % 5]
                cipher += c1 + c2
                pair_result["rule"] = "Même ligne → décalage à droite"
                pair_result["result"] = (c1 + c2).upper()
                steps["steps"].append(pair_result)
                break
        else:
            # Vérifier même colonne
            found_col = False
            for col in range(5):
                col_current = matrix[:, col]
                if pair[0] in col_current and pair[1] in col_current:
                    first_letter = list(col_current).index(pair[0])
                    second_letter = list(col_current).index(pair[1])
                    c1 = matrix[(first_letter + 1) % 5, col]
                    c2 = matrix[(second_letter + 1) % 5, col]
                    cipher += c1 + c2
                    pair_result["rule"] = "Même colonne → décalage en bas"
                    pair_result["result"] = (c1 + c2).upper()
                    steps["steps"].append(pair_result)
                    found_col = True
                    break
            
            if not found_col:
                # Rectangle
                first_pos = np.where(matrix == pair[0])
                second_pos = np.where(matrix == pair[1])
                c1 = matrix[first_pos[0][0], second_pos[1][0]]
                c2 = matrix[second_pos[0][0], first_pos[1][0]]
                cipher += c1 + c2
                pair_result["rule"] = "Rectangle → coins opposés"
                pair_result["result"] = (c1 + c2).upper()
                steps["steps"].append(pair_result)
    
    steps["ciphertext"] = cipher.upper()
    return steps


