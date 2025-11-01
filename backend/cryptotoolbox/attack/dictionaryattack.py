import time
from backend.cryptotoolbox.attack.utils import clean_text
from backend.cryptotoolbox.cyphers.plaiyfair import encrypt_playfair

def run_dictionary_attack(algorithm, encrypted, key_data, dictionary, start_time, max_seconds, limit, attempts):
    """
    Runs a dictionary attack.
    """
    matches = []
    timeout_reached = False
    limit_reached = False

    def record(plaintext: str, keyobj, confidence: str, notes: str):
        nonlocal matches
        cand = clean_text(plaintext)
        matches.append({
            'candidate_plaintext': cand,
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
                cipher = encrypt_playfair(kw, word).upper()

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
