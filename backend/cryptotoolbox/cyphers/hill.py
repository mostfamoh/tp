"""
Chiffrement de Hill - TP SSAD USTHB
Chiffrement matriciel utilisant l'algèbre linéaire modulo 26
Supporte matrices 2×2 et 3×3
"""
import numpy as np
from math import gcd


def clean_text(s: str) -> str:
    """Nettoie le texte: majuscules uniquement, supprime espaces et ponctuation."""
    return ''.join(ch for ch in s.upper() if ch.isalpha())


def mod_inv(d: int, m: int = 26) -> int:
    """Trouve l'inverse modulaire du déterminant modulo m."""
    for i in range(1, m):
        if (d * i) % m == 1:
            return i
    return 0


def inv_key_mod(key_matrix: np.ndarray, m: int = 26) -> np.ndarray:
    """Calcule l'inverse modulaire de la matrice clé."""
    det = int(round(np.linalg.det(key_matrix)))
    det_mod = det % m
    inv_det = mod_inv(det_mod, m)

    if inv_det == 0:
        raise ValueError("La matrice clé n'est pas inversible mod 26.")

    adj = np.round(det * np.linalg.inv(key_matrix)).astype(int) % m
    return (inv_det * adj) % m


def get_key_matrix_2x2(a: int, b: int, c: int, d: int) -> np.ndarray:
    """
    Crée une matrice 2×2 directement à partir des coefficients.
    
    Args:
        a, b, c, d (int): Coefficients de la matrice [[a,b],[c,d]]
    
    Returns:
        np.ndarray: Matrice 2×2
    """
    matrix = np.array([[a, b], [c, d]])
    
    # Vérifier que la matrice est inversible
    det = (a * d - b * c) % 26
    if gcd(det, 26) != 1:
        raise ValueError(f"Matrice non inversible: det={det}, gcd(det,26)={gcd(det,26)}")
    
    return matrix


def get_key_matrix_from_keyword(keyword: str, size: int = 3) -> np.ndarray:
    """Construit une matrice clé à partir d'un mot-clé."""
    keyword = clean_text(keyword)
    key_matrix = np.zeros((size, size), dtype=int)
    k = 0
    for i in range(size):
        for j in range(size):
            if k < len(keyword):
                key_matrix[i][j] = ord(keyword[k]) - 65
            else:
                key_matrix[i][j] = (k - len(keyword)) % 26
            k += 1
    return key_matrix


def hill_encrypt_2x2(plaintext: str, matrix: np.ndarray) -> str:
    """
    Chiffre avec Hill 2×2.
    
    Args:
        plaintext (str): Texte en clair
        matrix (np.ndarray): Matrice 2×2
    
    Returns:
        str: Texte chiffré
    """
    text = clean_text(plaintext)
    if len(text) % 2 == 1:
        text += 'X'  # Remplissage
    
    ciphertext = ""
    for i in range(0, len(text), 2):
        vector = np.array([[ord(text[i]) - 65], [ord(text[i+1]) - 65]])
        cipher_vector = np.dot(matrix, vector) % 26
        ciphertext += chr(int(cipher_vector[0][0]) + 65)
        ciphertext += chr(int(cipher_vector[1][0]) + 65)
    
    return ciphertext


def hill_decrypt_2x2(ciphertext: str, matrix: np.ndarray) -> str:
    """
    Déchiffre avec Hill 2×2.
    
    Args:
        ciphertext (str): Texte chiffré
        matrix (np.ndarray): Matrice 2×2 utilisée pour le chiffrement
    
    Returns:
        str: Texte en clair
    """
    text = clean_text(ciphertext)
    inv_matrix = inv_key_mod(matrix, 26)
    
    plaintext = ""
    for i in range(0, len(text), 2):
        vector = np.array([[ord(text[i]) - 65], [ord(text[i+1]) - 65]])
        plain_vector = np.dot(inv_matrix, vector) % 26
        plaintext += chr(int(plain_vector[0][0]) + 65)
        plaintext += chr(int(plain_vector[1][0]) + 65)
    
    return plaintext


def hill_encrypt(keyword: str, plaintext: str) -> str:
    """
    Chiffre avec Hill 3×3 en utilisant un mot-clé.
    
    Args:
        keyword (str): Mot-clé pour générer la matrice
        plaintext (str): Texte en clair
    
    Returns:
        str: Texte chiffré
    """
    key_matrix = get_key_matrix_from_keyword(keyword, 3)
    text = clean_text(plaintext)
    
    # Remplir si nécessaire
    while len(text) % 3 != 0:
        text += 'X'
    
    ciphertext = ""
    pos = 0
    while pos < len(text):
        block = np.array([[ord(text[pos]) - 65],
                         [ord(text[pos+1]) - 65],
                         [ord(text[pos+2]) - 65]])
        cipher_block = np.dot(key_matrix, block) % 26
        for i in range(3):
            ciphertext += chr(int(cipher_block[i][0]) + 65)
        pos += 3
    
    return ciphertext


def hill_decrypt(keyword: str, ciphertext: str) -> str:
    """
    Déchiffre avec Hill 3×3.
    
    Args:
        keyword (str): Mot-clé utilisé pour le chiffrement
        ciphertext (str): Texte chiffré
    
    Returns:
        str: Texte en clair
    """
    key_matrix = get_key_matrix_from_keyword(keyword, 3)
    try:
        inv_matrix = inv_key_mod(key_matrix, 26)
    except ValueError:
        return "Clé invalide (matrice non inversible mod 26)"

    text = clean_text(ciphertext)
    plaintext = ""
    pos = 0
    while pos < len(text):
        block = np.array([[ord(text[pos]) - 65],
                         [ord(text[pos+1]) - 65],
                         [ord(text[pos+2]) - 65]])
        plain_block = np.dot(inv_matrix, block) % 26
        for i in range(3):
            plaintext += chr(int(plain_block[i][0]) + 65)
        pos += 3
    
    return plaintext


def explain_steps_2x2(plaintext: str, matrix: np.ndarray) -> dict:
    """
    Explique les étapes du chiffrement Hill 2×2 (pour documentation/rapport).
    
    Args:
        plaintext (str): Texte à chiffrer
        matrix (np.ndarray): Matrice 2×2
    
    Returns:
        dict: Détails du chiffrement étape par étape
    """
    text = clean_text(plaintext)
    if len(text) % 2 == 1:
        text += 'X'
    
    det = int(np.linalg.det(matrix)) % 26
    try:
        inv_matrix = inv_key_mod(matrix, 26)
    except:
        inv_matrix = None
    
    steps = {
        "algorithm": "Hill 2×2",
        "plaintext": text,
        "key_matrix": matrix.tolist(),
        "determinant": det,
        "inverse_matrix": inv_matrix.tolist() if inv_matrix is not None else "Non inversible",
        "steps": [],
        "ciphertext": ""
    }
    
    cipher = ""
    for i in range(0, len(text), 2):
        vector = np.array([[ord(text[i]) - 65], [ord(text[i+1]) - 65]])
        cipher_vector = np.dot(matrix, vector) % 26
        c1 = chr(int(cipher_vector[0][0]) + 65)
        c2 = chr(int(cipher_vector[1][0]) + 65)
        cipher += c1 + c2
        
        steps["steps"].append({
            "digraph": text[i:i+2],
            "vector": vector.T.tolist()[0],
            "calculation": f"{matrix.tolist()} × {vector.T.tolist()[0]} mod 26 = {cipher_vector.T.tolist()[0]}",
            "result": c1 + c2
        })
    
    steps["ciphertext"] = cipher
    return steps


def explain_steps(keyword: str, plaintext: str) -> dict:
    """
    Explique les étapes du chiffrement Hill 3×3 (pour documentation/rapport).
    """
    key_matrix = get_key_matrix_from_keyword(keyword, 3)
    text = clean_text(plaintext)
    while len(text) % 3 != 0:
        text += 'X'
    
    steps = {
        "algorithm": "Hill 3×3",
        "keyword": keyword,
        "plaintext": text,
        "key_matrix": key_matrix.tolist(),
        "steps": [],
        "ciphertext": ""
    }
    
    cipher = ""
    pos = 0
    while pos < len(text):
        block = np.array([[ord(text[pos]) - 65],
                         [ord(text[pos+1]) - 65],
                         [ord(text[pos+2]) - 65]])
        cipher_block = np.dot(key_matrix, block) % 26
        trigraph = ""
        for i in range(3):
            trigraph += chr(int(cipher_block[i][0]) + 65)
        cipher += trigraph
        
        steps["steps"].append({
            "trigraph": text[pos:pos+3],
            "vector": block.T.tolist()[0],
            "result": trigraph
        })
        pos += 3
    
    steps["ciphertext"] = cipher
    return steps
