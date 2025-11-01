"""
Module principal cryptotoolbox - TP SSAD USTHB
Fonctions d'interface pour chiffrement/déchiffrement avec tous les algorithmes
"""
from .cyphers.caesar import caesar_encrypt, caesar_decrypt
from .cyphers.plaiyfair import encrypt_playfair, decrypt_playfair
from .cyphers.hill import hill_encrypt, hill_decrypt, hill_encrypt_2x2, hill_decrypt_2x2, get_key_matrix_2x2
from .cyphers.affine import encrypt_affine, decrypt_affine


def encrypt_with_algorithm(algorithm: str, text: str, key: dict) -> str:
    """
    Chiffre un texte avec l'algorithme spécifié.
    
    Args:
        algorithm (str): Nom de l'algorithme ('caesar', 'affine', 'playfair', 'hill')
        text (str): Texte en clair
        key (dict): Clé de chiffrement (format dépend de l'algorithme)
    
    Returns:
        str: Texte chiffré
    
    Raises:
        ValueError: Si l'algorithme est inconnu ou la clé invalide
    """
    algorithm = algorithm.lower()
    
    if algorithm in ("caesar", "cesar"):  # Support des deux orthographes
        return caesar_encrypt(text, key["shift"])
    
    elif algorithm in ("playfair", "plafair", "plaiyfair"):  # Support variantes orthographiques
        return encrypt_playfair(key["keyword"], text)
    
    elif algorithm == "affine":
        return encrypt_affine(text, key["a"], key["b"])
    
    elif algorithm == "hill":
        # Supporter les deux formats: matrice 2x2 directe ou mot-clé pour 3x3
        if "matrix" in key and isinstance(key["matrix"], list):
            # Format matrice 2x2: [[a,b],[c,d]]
            import numpy as np
            matrix = np.array(key["matrix"])
            if matrix.shape == (2, 2):
                return hill_encrypt_2x2(text, matrix)
            else:
                raise ValueError("Matrice Hill doit être 2x2 pour ce format")
        elif "keyword" in key:
            # Format mot-clé pour 3x3
            return hill_encrypt(key["keyword"], text)
        else:
            raise ValueError("Clé Hill doit contenir 'matrix' ou 'keyword'")
    
    else:
        raise ValueError(f"Algorithme inconnu: {algorithm}")


def decrypt_with_algorithm(algorithm: str, text: str, key: dict) -> str:
    """
    Déchiffre un texte avec l'algorithme spécifié.
    
    Args:
        algorithm (str): Nom de l'algorithme
        text (str): Texte chiffré
        key (dict): Clé de déchiffrement
    
    Returns:
        str: Texte en clair
    
    Raises:
        ValueError: Si l'algorithme est inconnu ou la clé invalide
    """
    algorithm = algorithm.lower()
    
    if algorithm in ("caesar", "cesar"):  # Support des deux orthographes
        return caesar_decrypt(text, key["shift"])
    
    elif algorithm in ("playfair", "plafair", "plaiyfair"):  # Support variantes orthographiques
        return decrypt_playfair(key["keyword"], text)
    
    elif algorithm == "affine":
        return decrypt_affine(text, key["a"], key["b"])
    
    elif algorithm == "hill":
        # Supporter les deux formats
        if "matrix" in key and isinstance(key["matrix"], list):
            import numpy as np
            matrix = np.array(key["matrix"])
            if matrix.shape == (2, 2):
                return hill_decrypt_2x2(text, matrix)
            else:
                raise ValueError("Matrice Hill doit être 2x2 pour ce format")
        elif "keyword" in key:
            return hill_decrypt(key["keyword"], text)
        else:
            raise ValueError("Clé Hill doit contenir 'matrix' ou 'keyword'")
    
    else:
        raise ValueError(f"Algorithme inconnu: {algorithm}")
    