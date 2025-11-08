
import time
import json
from math import gcd
from backend.cryptotoolbox.attack.utils import (
    caesar_decrypt, affine_decrypt, hill_decrypt_2x2, clean_text
)
from backend.cryptotoolbox.cyphers.plaiyfair import decrypt_playfair
from itertools import product
from typing import Optional, Tuple


def run_bruteforce_attack(algorithm, encrypted, limit, max_seconds, start_time, dictionary, playfair_keyspace):
    """
    Existing compatibility wrapper: keep the original brute-force by-keys behavior
    for supported classical algorithms. This function is left mostly unchanged to
    preserve behavior when called from `attack_runner.run_attack`.
    """
    attempts = 0
    matches = []
    timeout_reached = False
    limit_reached = False

    def _to_digits_if_possible(s: str):
        # Map A-J to 0-9; only return a digits string if all chars are within A-J
        if not s:
            return None
        mapping = {chr(ord('A') + i): str(i) for i in range(10)}
        out = []
        for ch in s.upper():
            if ch in mapping:
                out.append(mapping[ch])
            else:
                return None  # contains non-digit-encodable letters
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
        valid_a = [a for a in range(1, 26) if gcd(a, 26) == 1]
        for a, b in product(valid_a, range(26)):
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
        # iterate over all 2x2 matrices using a product generator (more concise)
        for a, b, c, d in product(range(26), repeat=4):
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
    else:
        return attempts, matches, limit_reached, timeout_reached, {'error': f'Unsupported algorithm for brute-force: {algorithm}'}

    return attempts, matches, limit_reached, timeout_reached, None


# ---------------------------------------------------------------------------
# New: plaintext brute-force helper (user-provided algorithm)
# ---------------------------------------------------------------------------

ALPHABET_PETIT = "012"  # cas longueur 3
ALPHABET_CHIFFRES = "0123456789"  # cas chiffres (longueur 6)
ALPHABET_LETTERS = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)
ALPHABET_ALPHANUM = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
)
ALPHABET_COMPLET = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "!@#$%&*()-_=+[]{};:,.?/<>;"
)


def choisir_alphabet(target: str) -> Optional[str]:
    """Return the alphabet to use depending on the length/content of target.

    If the length is not 3 or 6, returns None.
    """
    L = len(target)
    if L == 3:
        if all(ch in ALPHABET_PETIT for ch in target):
            # strictly in small 0-2 alphabet (course exercise)
            return ALPHABET_PETIT
        if all(ch in ALPHABET_CHIFFRES for ch in target):
            return ALPHABET_CHIFFRES
        if all(ch in ALPHABET_LETTERS for ch in target):
            return ALPHABET_LETTERS
        # mixed letters/digits for short target: allow alphanumeric only (no specials)
        return ALPHABET_ALPHANUM
    if L == 6:
        if all(ch in ALPHABET_CHIFFRES for ch in target):
            return ALPHABET_CHIFFRES
        if all(ch in ALPHABET_LETTERS for ch in target):
            return ALPHABET_ALPHANUM  # letters only => still allow digits to be safe
        # mixed letters/digits or contains specials -> allow full
        return ALPHABET_COMPLET
    else:
        return None


def brute_force_plaintext(target: str, show_progress_every: int = 500_000) -> Tuple[Optional[str], int, float]:
    """Brute-force plaintext candidates to match `target`.

    Returns a tuple (found_candidate or None, attempts, elapsed_seconds).
    This is intended as a standalone helper/CLI for educational use.
    """
    length = len(target)
    alphabet = choisir_alphabet(target)
    if alphabet not in {ALPHABET_PETIT, ALPHABET_CHIFFRES, ALPHABET_LETTERS, ALPHABET_ALPHANUM, ALPHABET_COMPLET}:
        print("Longueur du mot incorrecte or unsupported for plaintext brute force.")
        return None, 0, 0.0

    base = len(alphabet)
    total = base ** length

    print(f"\nMot cible : {target!r}")
    print(f"Alphabet de taille: {base}. Nombre de combinaisons possibles = {total:,}.")
    print("Début du brute force... (appuyez sur Ctrl+C pour arrêter)\n")

    start_ns = time.perf_counter_ns()
    tried = 0

    try:
        for tup in product(alphabet, repeat=length):
            tried += 1
            cand = ''.join(tup)
            if cand == target:
                end_ns = time.perf_counter_ns()
                elapsed_s = (end_ns - start_ns) / 1_000_000_000
                elapsed_ms = (end_ns - start_ns) / 1_000_000
                nb_essais_sec = tried / elapsed_s if elapsed_s > 0 else float('inf')
                print(f"\nTrouvé: {cand!r}")
                print(f"Nombre d'essais: {tried:,}")
                print(f"Temps écoulé: {elapsed_s:.6f} s ({elapsed_ms:.3f} ms)")
                print(f"Nombre d'essais moyen par seconde: {nb_essais_sec:,.0f} tests/s\n")
                return cand, tried, elapsed_s

            if show_progress_every and (tried % show_progress_every == 0):
                now_ns = time.perf_counter_ns()
                elapsed_s = (now_ns - start_ns) / 1_000_000_000
                nb_essais_sec = tried / elapsed_s if elapsed_s > 0 else float('inf')
                print(f"Nombre de tests: {tried:,} / {total:,} — ~{nb_essais_sec:,.0f} tests/s — temps écoulé: {elapsed_s:.3f}s")

    except KeyboardInterrupt:
        end_ns = time.perf_counter_ns()
        elapsed_s = (end_ns - start_ns) / 1_000_000_000
        print("\nProgramme interrompu.")
        print(f"Essais effectués: {tried:,}")
        print(f"Temps écoulé: {elapsed_s:.6f} s\n")
        return None, tried, elapsed_s

    end_ns = time.perf_counter_ns()
    elapsed_s = (end_ns - start_ns) / 1_000_000_000
    print("\nToutes les combinaisons ont été testés. Mot non trouvé.")
    print(f"Nombre total d'essai effectués: {tried:,}")
    print(f"Temps écoulé: {elapsed_s:.6f} s\n")
    return None, tried, elapsed_s


if __name__ == '__main__':
    # Provide two entrypoints: the original attack_runner-compatible CLI
    # (unchanged) expects a JSON instruction file, but for convenience
    # allow running the plaintext brute-force directly with `--plain`.
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == '--plain':
        # Usage: python bruteforce.py --plain
        tgt = input("Entrez le mot-cible: ").strip()
        if not tgt:
            print("Aucun mot entré.\n")
            sys.exit(0)
        brute_force_plaintext(tgt)
        print("Fin du programme.\n")
        sys.exit(0)

    # Fallback to original behaviour used by attack_runner
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: bruteforce.py <instruction.json> or --plain'}))
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        instr = json.load(f)
    # reuse run_attack from parent module if needed; this file is kept
    # compatible with previous CLI expectations by simply printing the
    # instruction (the real runner is attack_runner.py in this package).
    print(json.dumps({'info': 'Please run attack_runner.py for full attack orchestration', 'instruction': instr}, ensure_ascii=False, indent=2))
