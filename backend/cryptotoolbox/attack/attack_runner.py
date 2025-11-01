import json
import sqlite3
import time
import os
from typing import Dict, Any

from .bruteforce import run_bruteforce_attack
from .dictionaryattack import run_dictionary_attack
from .utils import clean_text


def load_user_from_sqlite(db_path: str, username: str) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    candidate_tables = [t for t in tables if 'customuser' in t.lower()]
    if not candidate_tables:
        raise RuntimeError('Could not find CustomUser table in sqlite DB')
    table = candidate_tables[0]
    cur.execute(f"SELECT * FROM {table} WHERE username = ?", (username,))
    row = cur.fetchone()
    if not row:
        return None
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    data = dict(zip(cols, row))
    conn.close()
    return {
        'username': data.get('username'),
        'password_encrypted': data.get('password_encrypted') or data.get('password_encypted'),
        'algorithm': data.get('algorithm'),
        'key_data': data.get('key_data'),
    }



def run_attack(instruction: Dict[str, Any]) -> Dict[str, Any]:
    target = instruction.get('target_username')
    mode = instruction.get('mode', 'both')
    algo_override = instruction.get('algorithm')
    limit = int(instruction.get('limit', 0))
    max_seconds = float(instruction.get('max_seconds', 0))
    dictionary = instruction.get('dictionary') or []
    playfair_keyspace = instruction.get('playfair_keyspace') or []
    
    start_all = time.perf_counter()
    attempts = 0
    matches = []
    timeout_reached = False
    limit_reached = False
    errors = []

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    test_users_file = os.path.join(repo_root, 'test_users.txt')
    
    auto_allowed_prefixes = ('test_', 'demo_', 'tmp_')
    is_auto_allowed = target and any(target.startswith(prefix) for prefix in auto_allowed_prefixes)

    if not is_auto_allowed:
        if os.path.exists(test_users_file):
            with open(test_users_file, 'r', encoding='utf-8') as f:
                allowed = {ln.strip() for ln in f if ln.strip()}
            if target not in allowed:
                return {'error': 'Operation aborted — unauthorized target (not in test_users.txt)'}
        else:
            return {'error': 'Operation aborted — unauthorized target. Create test_users.txt or use test_*/demo_*/tmp_* usernames.'}

    db_path = os.path.join(repo_root, 'db.sqlite3')
    try:
        user = load_user_from_sqlite(db_path, target)
    except Exception as e:
        return {'error': f'Failed to read local DB: {e}'}
    if not user:
        return {'error': 'User not found'}

    algorithm = (algo_override or user.get('algorithm') or '').lower().replace('plafair', 'playfair').replace('cesar', 'caesar')
    encrypted = user.get('password_encrypted')
    key_data_str = user.get('key_data', '{}')
    
    # Parser key_data (peut être double-encodé en JSON)
    key_data = key_data_str
    for _ in range(2):  # Essayer de parser jusqu'à 2 fois (double-encodage)
        if isinstance(key_data, str):
            try:
                key_data = json.loads(key_data)
            except (json.JSONDecodeError, ValueError):
                break
        else:
            break
    
    # S'assurer que c'est un dict
    if not isinstance(key_data, dict):
        key_data = {}


    do_dictionary = mode in ('dictionary', 'both')
    do_bruteforce = mode in ('bruteforce', 'both')

    if do_dictionary:
        dict_attempts, dict_matches, limit_reached, timeout_reached, err = run_dictionary_attack(
            algorithm, encrypted, key_data, dictionary, start_all, max_seconds, limit, attempts
        )
        attempts = dict_attempts
        matches.extend(dict_matches)
        if err: errors.append(err.get('error'))

    if do_bruteforce and not timeout_reached and not limit_reached:
        bf_attempts, bf_matches, limit_reached, timeout_reached, err = run_bruteforce_attack(
            algorithm, encrypted, limit, max_seconds, start_all, dictionary, playfair_keyspace
        )
        attempts += bf_attempts
        matches.extend(bf_matches)
        if err: errors.append(err.get('error'))

    elapsed = time.perf_counter() - start_all
    truncated = False
    total_matches = len(matches)
    if total_matches > 200:
        matches = matches[:200]
        truncated = True

    report = {
        'target_username': target,
        'algorithm': algorithm,
        'mode': mode,
        'attempts': attempts,
        'time_sec': round(elapsed, 6),
        'limit_reached': bool(limit_reached),
        'timeout_reached': bool(timeout_reached),
        'matches_count': total_matches,
        'matches': matches,
        'notes': ('Truncated results' if truncated else ''),
        'errors': errors
    }
    return report


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: attack_runner.py <instruction.json>'}))
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        instr = json.load(f)
    out = run_attack(instr)
    print(json.dumps(out, ensure_ascii=False, indent=2))
