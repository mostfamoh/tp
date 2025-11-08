import json
from backend.cryptotoolbox.attack.attack_runner import run_attack

instr = {
    'target_username': 'mostafa',
    'mode': 'both',
    'limit': 0,
    'max_seconds': 10
}
res = run_attack(instr)
print(json.dumps(res, ensure_ascii=False, indent=2))
