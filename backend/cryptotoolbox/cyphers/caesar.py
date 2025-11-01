"""
Chiffrement de César - TP SSAD USTHB
Algorithme de chiffrement par substitution monoalphabétique
avec décalage de n rangs dans l'alphabet.
"""


def clean_text(s: str) -> str:
    """Nettoie le texte: majuscules uniquement, supprime espaces et ponctuation."""
    return ''.join(ch for ch in s.upper() if ch.isalpha())


def caesar_encrypt(plain_text: str, shift: int) -> str:
    """
    Chiffre un texte avec le chiffrement de César.
    
    Args:
        plain_text (str): Texte en clair
        shift (int): Décalage (0-25)
    
    Returns:
        str: Texte chiffré
    
    Exemple:
        >>> caesar_encrypt("HELLO", 3)
        'KHOOR'
    """
    text = clean_text(plain_text)
    cipher = ''
    for ch in text:
        new_index = (ord(ch) - ord('A') + shift) % 26
        cipher += chr(new_index + ord('A'))
    return cipher


def caesar_decrypt(cipher_text: str, shift: int) -> str:
    """
    Déchiffre un texte chiffré avec César.
    
    Args:
        cipher_text (str): Texte chiffré
        shift (int): Décalage utilisé pour le chiffrement
    
    Returns:
        str: Texte en clair
    
    Exemple:
        >>> caesar_decrypt("KHOOR", 3)
        'HELLO'
    """
    text = clean_text(cipher_text)
    plain = ''
    for ch in text:
        new_index = (ord(ch) - ord('A') - shift) % 26
        plain += chr(new_index + ord('A'))
    return plain


def explain_steps(plain_text: str, shift: int) -> dict:
    """
    Explique les étapes du chiffrement César (pour documentation/rapport).
    
    Args:
        plain_text (str): Texte à chiffrer
        shift (int): Décalage
    
    Returns:
        dict: Détails du chiffrement étape par étape
    """
    text = clean_text(plain_text)
    steps = {
        "algorithm": "César",
        "plaintext": text,
        "shift": shift,
        "steps": [],
        "ciphertext": ""
    }
    
    cipher = ''
    for i, ch in enumerate(text):
        original_index = ord(ch) - ord('A')
        new_index = (original_index + shift) % 26
        cipher_char = chr(new_index + ord('A'))
        cipher += cipher_char
        
        steps["steps"].append({
            "position": i + 1,
            "char": ch,
            "index": original_index,
            "formula": f"({original_index} + {shift}) mod 26 = {new_index}",
            "result": cipher_char
        })
    
    steps["ciphertext"] = cipher
    return steps 


