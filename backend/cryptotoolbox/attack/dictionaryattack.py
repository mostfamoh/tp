import time
from backend.cryptotoolbox.attack.utils import clean_text, convert_to_alpha
from backend.cryptotoolbox.cyphers.plaiyfair import encrypt_playfair

def number_to_letters(num_str):
    """
    Convertit une chaîne de chiffres en lettres pour Playfair.
    Exemple: "012" -> "ZEROONETWO", "123" -> "ONETWOTHREE"
    
    NOTE: Cette fonction n'est plus utilisée pour Playfair.
    Utilisez convert_to_alpha() à la place pour la compatibilité.
    """
    digit_map = {
        '0': 'ZERO', '1': 'ONE', '2': 'TWO', '3': 'THREE', '4': 'FOUR',
        '5': 'FIVE', '6': 'SIX', '7': 'SEVEN', '8': 'EIGHT', '9': 'NINE'
    }
    result = ''
    for digit in str(num_str):
        if digit in digit_map:
            result += digit_map[digit]
        elif digit.isalpha():
            result += digit.upper()
    return result if result else num_str

def run_dictionary_attack(algorithm, encrypted, key_data, dictionary, start_time, max_seconds, limit, attempts):
    """
    Runs a dictionary attack.
    """
    matches = []
    timeout_reached = False
    limit_reached = False

    def _to_digits_if_possible(s: str):
        if not s:
            return None
        mapping = {chr(ord('A') + i): str(i) for i in range(10)}
        out = []
        for ch in s.upper():
            if ch in mapping:
                out.append(mapping[ch])
            else:
                return None
        return ''.join(out)

    def record(plaintext: str, keyobj, confidence: str, notes: str):
        nonlocal matches
        cand_raw = plaintext
        cand = clean_text(plaintext)
        cand_digits = _to_digits_if_possible(cand)
        matches.append({
            'candidate_plaintext': cand,
            'candidate_plaintext_raw': cand_raw,
            'candidate_plaintext_digits': cand_digits,
            'candidate_key': keyobj,
            'confidence': confidence,
            'notes': notes
        })

    if not dictionary:
        return attempts, matches, limit_reached, timeout_reached, None

    for word in dictionary:
        if max_seconds and (time.perf_counter() - start_time) > max_seconds:
            timeout_reached = True
            break
        if limit and attempts >= limit:
            limit_reached = True
            break
        attempts += 1
        cipher = ''
        try:
            if algorithm == 'caesar':
                shift = key_data.get('shift') if isinstance(key_data, dict) else None
                if shift is None: continue
                from string import ascii_uppercase
                txt = clean_text(word)
                cipher = ''.join(ascii_uppercase[(ord(ch) - 65 + shift) % 26] for ch in txt)
            
            elif algorithm == 'affine':
                if not isinstance(key_data, dict): continue
                a = int(key_data.get('a'))
                b = int(key_data.get('b'))
                txt = clean_text(word)
                cipher = ''.join(chr(((a * (ord(ch) - 65) + b) % 26) + 65) for ch in txt)

            elif algorithm == 'playfair':
                kw = key_data.get('keyword') if isinstance(key_data, dict) else None
                if not kw: continue
                # Utiliser convert_to_alpha pour la compatibilité (0->A, 1->B, etc.)
                word_alpha = convert_to_alpha(word)
                cipher = encrypt_playfair(kw, word_alpha).upper()

            elif algorithm == 'hill':
                mat = key_data.get('matrix') if isinstance(key_data, dict) else None
                if not mat: continue
                txt = clean_text(word)
                if len(txt) % 2 == 1: txt += 'X'
                cipher = ''
                a, b = mat[0]
                c, d = mat[1]
                for i in range(0, len(txt), 2):
                    x0, x1 = ord(txt[i]) - 65, ord(txt[i+1]) - 65
                    y0 = (a * x0 + b * x1) % 26
                    y1 = (c * x0 + d * x1) % 26
                    cipher += chr(y0 + 65) + chr(y1 + 65)
            
            else:
                continue

        except Exception:
            continue

        if cipher and clean_text(cipher) == clean_text(encrypted):
            confidence = 'high' if clean_text(word) in [clean_text(d) for d in dictionary] else 'medium'
            record(word, {'password_candidate': word}, confidence, 'Dictionary encryption matched stored ciphertext')

    return attempts, matches, limit_reached, timeout_reached, None
