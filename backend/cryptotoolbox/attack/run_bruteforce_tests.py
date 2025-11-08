"""Small test runner for the project's brute-force helpers.

This script runs a few quick sanity checks (non-exhaustive) to validate the
changes made to `bruteforce.py`.

Usage:
    python run_bruteforce_tests.py

"""
from backend.cryptotoolbox.attack.bruteforce import (
    choisir_alphabet,
    brute_force_plaintext,
)


def test_choisir_alphabet():
    assert choisir_alphabet('012') == "012"
    assert choisir_alphabet('123456') == "0123456789"
    assert choisir_alphabet('abcDEF') == "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*()-_=+[]{};:,.?/<>;"
    assert choisir_alphabet('') is None
    print('choisir_alphabet: OK')


def test_brute_force_plaintext():
    # small test: target within ALPHABET_PETIT
    found, attempts, elapsed = brute_force_plaintext('012', show_progress_every=1000000)
    assert found == '012'
    assert attempts >= 1
    assert elapsed >= 0.0
    print('brute_force_plaintext (small): OK')


if __name__ == '__main__':
    test_choisir_alphabet()
    test_brute_force_plaintext()
    print('All tests passed.')
