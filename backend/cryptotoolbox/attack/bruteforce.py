
import time
from math import gcd
from backend.cryptotoolbox.attack.utils import (
    caesar_decrypt, affine_decrypt, hill_decrypt_2x2, clean_text
)
from backend.cryptotoolbox.cyphers.plaiyfair import decrypt_playfair

def run_bruteforce_attack(algorithm, encrypted, limit, max_seconds, start_time, dictionary, playfair_keyspace):
    """
    Runs a brute-force attack for the specified algorithm.
    """
    attempts = 0
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

    if algorithm == 'caesar':
        for s in range(26):
            if max_seconds and (time.perf_counter() - start_time) > max_seconds:
                timeout_reached = True
                break
            if limit and attempts >= limit:
                limit_reached = True
                break
            attempts += 1
            try:
                guess = caesar_decrypt(encrypted, s)
                if guess.isalpha() and len(guess) >= 3:
                    confidence = 'low'
                    if any(clean_text(guess) == clean_text(w) for w in dictionary):
                        confidence = 'high'
                    record(guess, {'shift': s}, confidence, 'Alphabetic candidate')
            except Exception:
                continue

    elif algorithm == 'affine':
        for a in range(1, 26):
            if gcd(a, 26) != 1:
                continue
            for b in range(26):
                if max_seconds and (time.perf_counter() - start_time) > max_seconds:
                    timeout_reached = True
                    break
                if limit and attempts >= limit:
                    limit_reached = True
                    break
                attempts += 1
                try:
                    guess = affine_decrypt(encrypted, a, b)
                    if guess.isalpha() and len(guess) >= 3:
                        confidence = 'low'
                        if any(clean_text(guess) == clean_text(w) for w in dictionary):
                            confidence = 'high'
                        record(guess, {'a': a, 'b': b}, confidence, 'Alphabetic candidate')
                except Exception:
                    continue
            if timeout_reached or limit_reached:
                break

    elif algorithm == 'playfair':
        if not playfair_keyspace:
            return attempts, matches, limit_reached, timeout_reached, {'error': 'Playfair keyspace required for brute-force.'}
        for kw in playfair_keyspace:
            if max_seconds and (time.perf_counter() - start_time) > max_seconds:
                timeout_reached = True
                break
            if limit and attempts >= limit:
                limit_reached = True
                break
            attempts += 1
            try:
                guess = decrypt_playfair(kw, encrypted.lower())
                guess_norm = clean_text(guess)
                if guess_norm.isalpha() and len(guess_norm) >= 3:
                    confidence = 'low'
                    if any(guess_norm == clean_text(w) for w in dictionary):
                        confidence = 'high'
                    record(guess, {'keyword': kw}, confidence, 'Alphabetic candidate')
            except Exception:
                continue

    elif algorithm == 'hill':
        for a in range(26):
            for b in range(26):
                for c in range(26):
                    for d in range(26):
                        if max_seconds and (time.perf_counter() - start_time) > max_seconds:
                            timeout_reached = True
                            break
                        if limit and attempts >= limit:
                            limit_reached = True
                            break
                        attempts += 1
                        det = (a * d - b * c) % 26
                        if gcd(det, 26) != 1:
                            continue
                        try:
                            guess = hill_decrypt_2x2(encrypted, [[a, b], [c, d]])
                            if guess.isalpha() and len(guess) >= 3:
                                confidence = 'low'
                                if any(clean_text(guess) == clean_text(w) for w in dictionary):
                                    confidence = 'high'
                                record(guess, {'matrix': [[a, b], [c, d]]}, confidence, 'Alphabetic candidate')
                        except Exception:
                            continue
                    if timeout_reached or limit_reached: break
                if timeout_reached or limit_reached: break
            if timeout_reached or limit_reached: break
    
    else:
        return attempts, matches, limit_reached, timeout_reached, {'error': f'Unsupported algorithm for brute-force: {algorithm}'}

    return attempts, matches, limit_reached, timeout_reached, None
