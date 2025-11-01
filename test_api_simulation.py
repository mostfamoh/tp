"""
Test complet de l'API
"""
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from backend.cryptotoolbox.attack.attack_runner import run_attack

# Simuler ce que fait api_attack_full_dictionary
payload = {
    "target_username": "bellia",
    "max_seconds": 60,
    "limit": 0
}

# Charger le dictionnaire depuis le fichier
dict_type = payload.get('dictionary_type', 'default')

# Déterminer le chemin du dictionnaire
base_dir = os.path.dirname(__file__)

if dict_type == '012':
    dict_path = os.path.join(base_dir, 'backend', 'dictionaries', 'dict_012.txt')
elif dict_type == 'digits3':
    dict_path = os.path.join(base_dir, 'backend', 'dictionaries', 'dict_digits3.txt')
elif dict_type == 'digits6':
    dict_path = os.path.join(base_dir, 'backend', 'dictionaries', 'dict_digits6.txt')
elif dict_type == 'test':
    dict_path = os.path.join(base_dir, 'backend', 'dictionaries', 'dict_test.txt')
else:
    # Par défaut, utiliser backend/dic.txt
    dict_path = os.path.join(base_dir, 'backend', 'dic.txt')

print(f"Chemin dictionnaire: {dict_path}")
print(f"Existe? {os.path.exists(dict_path)}")

if os.path.exists(dict_path):
    with open(dict_path, 'r', encoding='utf-8') as f:
        dictionary = [line.strip() for line in f if line.strip()]
    
    print(f"Taille dictionnaire: {len(dictionary)}")
    print(f"Premiers éléments: {dictionary[:5]}")
    
    # Ajouter le dictionnaire au payload
    payload['mode'] = 'dictionary'
    payload['dictionary'] = dictionary
    
    print("\nTest de run_attack()...")
    try:
        result = run_attack(payload)
        print(f"✅ Succès!")
        print(f"Matches: {len(result.get('matches', []))}")
        
        # Ajouter des métadonnées sur le dictionnaire utilisé
        result['dictionary_info'] = {
            'type': dict_type,
            'path': dict_path,
            'size': len(dictionary)
        }
        
        print(f"✅ Métadonnées ajoutées!")
        print(f"Result keys: {result.keys()}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Fichier dictionnaire introuvable!")
