from math import gcd
from typing import List
from backend.cryptotoolbox.cyphers.plaiyfair import decrypt_playfair

def convert_to_alpha(text: str) -> str:
    """Converts digits to letters (0->A, 1->B,...) and keeps other letters."""
    result = []
    for char in text.upper():
        if '0' <= char <= '9':
            result.append(chr(ord('A') + int(char)))
        elif 'A' <= char <= 'Z':
            result.append(char)
    return "".join(result)

def clean_text(s: str) -> str:
    """Removes non-alphanumeric characters, converts digits to letters, and returns uppercase."""
    return convert_to_alpha(s)

def caesar_decrypt(cipher: str, shift: int) -> str:
    """Decrypts a Caesar cipher."""
    text = clean_text(cipher)
    plain = ''
    for ch in text:
        new_index = (ord(ch) - ord('A') - shift) % 26
        plain += chr(new_index + ord('A'))
    return plain

def affine_decrypt(cipher: str, a: int, b: int) -> str:
    """Decrypts an Affine cipher."""
    if gcd(a, 26) != 1:
        raise ValueError('a is not invertible mod 26')
    a_inv = pow(a, -1, 26)
    text = clean_text(cipher)
    plain = ''
    for ch in text:
        y = ord(ch) - ord('A')
        x = (a_inv * (y - b)) % 26
        plain += chr(x + ord('A'))
    return plain

def hill_decrypt_2x2(cipher: str, matrix: List[List[int]]) -> str:
    """Decrypts a 2x2 Hill cipher."""
    a, b = matrix[0]
    c, d = matrix[1]
    det = (a * d - b * c) % 26
    if gcd(det, 26) != 1:
        raise ValueError('Matrix is not invertible mod 26')
    det_inv = pow(det, -1, 26)
    
    inv00 = (det_inv * d) % 26
    inv01 = (det_inv * -b) % 26
    inv10 = (det_inv * -c) % 26
    inv11 = (det_inv * a) % 26

    text = clean_text(cipher)
    if len(text) % 2 == 1:
        text += 'X'
    
    plain = ''
    for i in range(0, len(text), 2):
        y0 = ord(text[i]) - ord('A')
        y1 = ord(text[i + 1]) - ord('A')
        x0 = (inv00 * y0 + inv01 * y1) % 26
        x1 = (inv10 * y0 + inv11 * y1) % 26
        plain += chr(x0 + ord('A')) + chr(x1 + ord('A'))
    return plain
