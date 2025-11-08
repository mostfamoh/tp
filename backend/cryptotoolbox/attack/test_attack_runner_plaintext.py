"""Test attack_runner integration for plaintext brute-force shortcut.

This script calls run_attack with an instruction that uses the override field so
we don't need to modify the sqlite DB.
"""
from backend.cryptotoolbox.attack.attack_runner import run_attack

instr = {
    'target_username': 'test_012',
    'mode': 'both',
    'algorithm': 'plaintext',
    'password_encrypted_override': '012',
    'limit': 0,
    'max_seconds': 10,
}

res = run_attack(instr)
import json
print(json.dumps(res, ensure_ascii=False, indent=2))
