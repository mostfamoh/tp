import os, json
from backend.cryptotoolbox.attack.attack_runner import load_user_from_sqlite
from backend.cryptotoolbox import encrypt_with_algorithm
from backend.cryptotoolbox.cyphers.caesar import caesar_decrypt, caesar_encrypt

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
db_path = os.path.join(repo_root, 'db.sqlite3')
username = 'mostafa'

print('DB path:', db_path)
try:
    user = load_user_from_sqlite(db_path, username)
except Exception as e:
    print('Failed to load user from sqlite:', e)
    raise SystemExit(1)

print('User record:')
print(json.dumps(user, ensure_ascii=False, indent=2))

enc = user.get('password_encrypted') or user.get('password_encypted')
print('stored encrypted:', enc)
algo = user.get('algorithm')
print('algorithm:', algo)
key = user.get('key_data') or {}
print('raw key_data:', key)

# Try Caesar quick test if algorithm contains 'caesar' or 'cesar'
if algo and 'cesar' in algo or (isinstance(algo, str) and 'caesar' in algo):
    # if key is dict find shift
    shift = None
    if isinstance(key, dict):
        shift = key.get('shift')
    try:
        print('Trying direct encryption of "aaaaaa":')
        print('encrypt_with_algorithm ->', encrypt_with_algorithm('caesar', 'aaaaaa', {'shift': shift}))
    except Exception as e:
        print('encrypt_with_algorithm failed:', e)

    print('Try decrypt candidates:')
    for s in range(26):
        try:
            g = caesar_decrypt(enc, s)
        except Exception as e:
            g = f'error: {e}'
        print(f'shift {s}: {g}')
