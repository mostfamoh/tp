"""
Stéganographie dans le texte
Techniques : Zero-Width Characters, WhiteSpace, Format-Based
"""


def hide_text_in_text(cover_text, secret_message, method='whitespace'):
    """
    Cache un message secret dans un texte de couverture
    
    Args:
        cover_text: Texte visible qui servira de couverture
        secret_message: Message secret à cacher
        method: Méthode à utiliser ('whitespace', 'zerowidth', 'case')
    
    Returns:
        dict: {
            'stego_text': texte avec message caché,
            'method': méthode utilisée,
            'cover_length': longueur du texte de couverture,
            'secret_length': longueur du message secret
        }
    """
    if method == 'whitespace':
        return _hide_whitespace(cover_text, secret_message)
    elif method == 'zerowidth':
        return _hide_zerowidth(cover_text, secret_message)
    elif method == 'case':
        return _hide_case(cover_text, secret_message)
    else:
        raise ValueError(f"Méthode inconnue: {method}")


def extract_text_from_text(stego_text, method='whitespace'):
    """
    Extrait un message secret d'un texte stéganographié
    
    Args:
        stego_text: Texte contenant le message caché
        method: Méthode utilisée pour cacher le message
    
    Returns:
        dict: {
            'secret_message': message extrait,
            'method': méthode utilisée,
            'success': bool
        }
    """
    if method == 'whitespace':
        return _extract_whitespace(stego_text)
    elif method == 'zerowidth':
        return _extract_zerowidth(stego_text)
    elif method == 'case':
        return _extract_case(stego_text)
    else:
        raise ValueError(f"Méthode inconnue: {method}")


# ============= MÉTHODE 1 : WHITESPACE =============

def _hide_whitespace(cover_text, secret_message):
    """
    Cache le message en utilisant des espaces et des tabulations
    0 = espace, 1 = tabulation
    """
    # Convertir le message en binaire
    binary = ''.join(format(ord(char), '08b') for char in secret_message)
    
    # Ajouter un marqueur de fin
    binary += '00000000'  # NULL character pour marquer la fin
    
    # Convertir binaire en espaces/tabs
    hidden = ''
    for bit in binary:
        if bit == '0':
            hidden += ' '  # Espace
        else:
            hidden += '\t'  # Tabulation
    
    # Insérer les espaces cachés après chaque phrase du texte
    sentences = cover_text.split('. ')
    if len(sentences) > 1:
        stego_text = sentences[0] + '.' + hidden + ' ' + '. '.join(sentences[1:])
    else:
        stego_text = cover_text + hidden
    
    return {
        'stego_text': stego_text,
        'method': 'whitespace',
        'cover_length': len(cover_text),
        'secret_length': len(secret_message),
        'binary_length': len(binary),
        'explanation': 'Message caché en utilisant des espaces et tabulations (invisible)'
    }


def _extract_whitespace(stego_text):
    """
    Extrait le message caché dans les espaces/tabulations
    """
    # Chercher les séquences d'espaces et de tabulations
    hidden = ''
    for char in stego_text:
        if char == ' ':
            hidden += '0'
        elif char == '\t':
            hidden += '1'
    
    # Convertir le binaire en texte
    message = ''
    i = 0
    while i + 8 <= len(hidden):
        byte = hidden[i:i+8]
        char_code = int(byte, 2)
        
        if char_code == 0:  # Marqueur de fin
            break
        
        if 32 <= char_code <= 126:  # Caractères ASCII imprimables
            message += chr(char_code)
        
        i += 8
    
    return {
        'secret_message': message,
        'method': 'whitespace',
        'success': len(message) > 0,
        'binary_extracted': len(hidden)
    }


# ============= MÉTHODE 2 : ZERO-WIDTH CHARACTERS =============

def _hide_zerowidth(cover_text, secret_message):
    """
    Cache le message en utilisant des caractères de largeur nulle
    ZERO WIDTH SPACE (U+200B), ZERO WIDTH NON-JOINER (U+200C), ZERO WIDTH JOINER (U+200D)
    """
    ZWS = '\u200B'   # Zero Width Space
    ZWNJ = '\u200C'  # Zero Width Non-Joiner
    ZWJ = '\u200D'   # Zero Width Joiner
    
    # Convertir le message en binaire
    binary = ''.join(format(ord(char), '08b') for char in secret_message)
    
    # Convertir binaire en caractères invisibles (base 3)
    hidden = ''
    for i in range(0, len(binary), 2):
        bits = binary[i:i+2]
        if bits == '00':
            hidden += ZWS
        elif bits == '01':
            hidden += ZWNJ
        elif bits == '10':
            hidden += ZWJ
        elif bits == '11':
            hidden += ZWS + ZWNJ  # Combinaison pour '11'
    
    # Ajouter un marqueur de fin
    hidden += ZWS + ZWS + ZWS  # Triple ZWS = fin
    
    # Insérer dans le texte (entre les mots)
    words = cover_text.split(' ')
    if len(words) > 2:
        stego_text = ' '.join(words[:2]) + hidden + ' ' + ' '.join(words[2:])
    else:
        stego_text = cover_text + hidden
    
    return {
        'stego_text': stego_text,
        'method': 'zerowidth',
        'cover_length': len(cover_text),
        'secret_length': len(secret_message),
        'hidden_chars': len(hidden),
        'explanation': 'Message caché avec caractères invisibles (U+200B, U+200C, U+200D)'
    }


def _extract_zerowidth(stego_text):
    """
    Extrait le message des caractères de largeur nulle
    """
    ZWS = '\u200B'
    ZWNJ = '\u200C'
    ZWJ = '\u200D'
    
    # Extraire les caractères invisibles
    hidden = ''
    for char in stego_text:
        if char in [ZWS, ZWNJ, ZWJ]:
            hidden += char
    
    # Détecter la fin (triple ZWS)
    end_marker = ZWS + ZWS + ZWS
    if end_marker in hidden:
        hidden = hidden[:hidden.index(end_marker)]
    
    # Convertir en binaire
    binary = ''
    i = 0
    while i < len(hidden):
        if i + 1 < len(hidden) and hidden[i] == ZWS and hidden[i+1] == ZWNJ:
            binary += '11'
            i += 2
        elif hidden[i] == ZWS:
            binary += '00'
            i += 1
        elif hidden[i] == ZWNJ:
            binary += '01'
            i += 1
        elif hidden[i] == ZWJ:
            binary += '10'
            i += 1
        else:
            i += 1
    
    # Convertir binaire en texte
    message = ''
    for i in range(0, len(binary), 8):
        if i + 8 <= len(binary):
            byte = binary[i:i+8]
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:
                message += chr(char_code)
    
    return {
        'secret_message': message,
        'method': 'zerowidth',
        'success': len(message) > 0,
        'chars_found': len(hidden)
    }


# ============= MÉTHODE 3 : CASE-BASED (Majuscules/minuscules) =============

def _hide_case(cover_text, secret_message):
    """
    Cache le message en modifiant la casse des lettres
    Majuscule = 1, Minuscule = 0
    """
    # Convertir le message en binaire
    binary = ''.join(format(ord(char), '08b') for char in secret_message)
    
    # Extraire les lettres modifiables du texte
    letters = [(i, char) for i, char in enumerate(cover_text) if char.isalpha()]
    
    if len(letters) < len(binary):
        raise ValueError(f"Texte trop court pour cacher le message (besoin de {len(binary)} lettres, disponibles: {len(letters)})")
    
    # Créer le texte stéganographié
    stego = list(cover_text)
    for i, bit in enumerate(binary):
        letter_index, letter = letters[i]
        if bit == '1':
            stego[letter_index] = letter.upper()
        else:
            stego[letter_index] = letter.lower()
    
    return {
        'stego_text': ''.join(stego),
        'method': 'case',
        'cover_length': len(cover_text),
        'secret_length': len(secret_message),
        'letters_used': len(binary),
        'letters_available': len(letters),
        'explanation': 'Message caché dans la casse des lettres (MAJ=1, min=0)'
    }


def _extract_case(stego_text):
    """
    Extrait le message de la casse des lettres
    """
    # Extraire le binaire de la casse
    binary = ''
    for char in stego_text:
        if char.isalpha():
            if char.isupper():
                binary += '1'
            else:
                binary += '0'
    
    # Convertir binaire en texte
    message = ''
    for i in range(0, len(binary), 8):
        if i + 8 <= len(binary):
            byte = binary[i:i+8]
            char_code = int(byte, 2)
            
            # Arrêter si on trouve un NULL ou caractère invalide
            if char_code == 0 or char_code > 126:
                break
            
            if 32 <= char_code <= 126:
                message += chr(char_code)
    
    return {
        'secret_message': message,
        'method': 'case',
        'success': len(message) > 0,
        'binary_length': len(binary)
    }


# ============= FONCTIONS UTILITAIRES =============

def get_available_methods():
    """
    Retourne la liste des méthodes disponibles avec leurs descriptions
    """
    return {
        'whitespace': {
            'name': 'WhiteSpace',
            'description': 'Cache le message dans des espaces et tabulations invisibles',
            'visibility': 'Invisible',
            'robustness': 'Faible (sensible au formatage)',
            'capacity': 'Illimitée'
        },
        'zerowidth': {
            'name': 'Zero-Width Characters',
            'description': 'Utilise des caractères Unicode invisibles (U+200B, U+200C, U+200D)',
            'visibility': 'Totalement invisible',
            'robustness': 'Moyenne',
            'capacity': 'Élevée'
        },
        'case': {
            'name': 'Case-Based',
            'description': 'Encode le message dans la casse des lettres (MAJ/min)',
            'visibility': 'Partiellement visible',
            'robustness': 'Élevée',
            'capacity': 'Limitée par le nombre de lettres'
        }
    }


def analyze_cover_text(text):
    """
    Analyse la capacité d'un texte à cacher des messages
    """
    letters = sum(1 for c in text if c.isalpha())
    words = len(text.split())
    sentences = text.count('.') + text.count('!') + text.count('?')
    
    return {
        'total_length': len(text),
        'letters': letters,
        'words': words,
        'sentences': sentences,
        'capacity_case': letters // 8,  # Caractères cachables avec case-based
        'capacity_whitespace': 'unlimited',
        'capacity_zerowidth': 'unlimited'
    }
