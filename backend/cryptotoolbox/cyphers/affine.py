"""
Chiffrement Affine - TP SSAD USTHB
Y = (aX + b) mod 26
où a doit être copremier avec 26 (gcd(a, 26) = 1)
Valeurs valides pour a: 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25
"""
from math import gcd


def clean_text(s: str) -> str:
    """Nettoie le texte: majuscules uniquement, supprime espaces et ponctuation."""
    return ''.join(ch for ch in s.upper() if ch.isalpha())


def mod_inverse(a: int, m: int = 26) -> int:
    """
    Calcule l'inverse modulaire de a modulo m.
    
    Args:
        a (int): Nombre dont on cherche l'inverse
        m (int): Modulo (par défaut 26)
    
    Returns:
        int: Inverse modulaire de a mod m
    
    Raises:
        ValueError: Si a n'a pas d'inverse (gcd(a,m) != 1)
    """
    if gcd(a, m) != 1:
        raise ValueError(f"{a} n'est pas copremier avec {m}, pas d'inverse modulaire")
    
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    raise ValueError(f"Impossible de trouver l'inverse de {a} mod {m}")


def encrypt_affine(plain_text: str, a: int, b: int) -> str:
    """
    Chiffre un texte avec le chiffrement affine.
    
    Formule: Y = (aX + b) mod 26
    
    Args:
        plain_text (str): Texte en clair
        a (int): Coefficient multiplicatif (doit être copremier avec 26)
        b (int): Décalage additif (0-25)
    
    Returns:
        str: Texte chiffré
    
    Exemple:
        >>> encrypt_affine("HELLO", 5, 8)
        'RCLLA'
    """
    if gcd(a, 26) != 1:
        raise ValueError(f"a={a} doit être copremier avec 26. Valeurs valides: 1,3,5,7,9,11,15,17,19,21,23,25")
    
    text = clean_text(plain_text)
    cipher = ''
    
    for ch in text:
        x = ord(ch) - ord('A')
        y = (a * x + b) % 26
        cipher += chr(y + ord('A'))
    
    return cipher


def decrypt_affine(cipher_text: str, a: int, b: int) -> str:
    """
    Déchiffre un texte chiffré avec affine.
    
    Formule: X = a_inv * (Y - b) mod 26
    
    Args:
        cipher_text (str): Texte chiffré
        a (int): Coefficient multiplicatif utilisé pour le chiffrement
        b (int): Décalage additif utilisé pour le chiffrement
    
    Returns:
        str: Texte en clair
    
    Exemple:
        >>> decrypt_affine("RCLLA", 5, 8)
        'HELLO'
    """
    if gcd(a, 26) != 1:
        raise ValueError(f"a={a} doit être copremier avec 26")
    
    text = clean_text(cipher_text)
    plain = ''
    a_inv = mod_inverse(a, 26)
    
    for ch in text:
        y = ord(ch) - ord('A')
        x = (a_inv * (y - b)) % 26
        plain += chr(x + ord('A'))
    
    return plain


def explain_steps(plain_text: str, a: int, b: int) -> dict:
    """
    Explique les étapes du chiffrement Affine (pour documentation/rapport).
    
    Args:
        plain_text (str): Texte à chiffrer
        a (int): Coefficient multiplicatif
        b (int): Décalage additif
    
    Returns:
        dict: Détails du chiffrement étape par étape
    """
    if gcd(a, 26) != 1:
        return {"error": f"a={a} n'est pas copremier avec 26"}
    
    text = clean_text(plain_text)
    steps = {
        "algorithm": "Affine",
        "plaintext": text,
        "a": a,
        "b": b,
        "formula": "Y = (aX + b) mod 26",
        "a_inverse": mod_inverse(a, 26),
        "decrypt_formula": f"X = {mod_inverse(a, 26)} * (Y - {b}) mod 26",
        "steps": [],
        "ciphertext": ""
    }
    
    cipher = ''
    for i, ch in enumerate(text):
        x = ord(ch) - ord('A')
        y = (a * x + b) % 26
        cipher_char = chr(y + ord('A'))
        cipher += cipher_char
        
        steps["steps"].append({
            "position": i + 1,
            "char": ch,
            "x": x,
            "calculation": f"({a} * {x} + {b}) mod 26 = {y}",
            "result": cipher_char
        })
    
    steps["ciphertext"] = cipher
    return steps
