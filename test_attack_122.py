"""
Test de l'attaque sur l'utilisateur avec mot de passe 122
"""
import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox.attack.attack_runner import run_attack

print("="*80)
print(" TEST ATTAQUE SUR MOT DE PASSE 122")
print("="*80)

# Chercher l'utilisateur
print("\n1. Recherche de l'utilisateur avec mot de passe 122...")
users_with_122 = CustomUser.objects.filter(password_encypted__icontains='BCC')  # 122 -> BCC -> ...

print(f"\nUtilisateurs trouvés avec '122' potentiel:")
all_users = CustomUser.objects.all()
for user in all_users:
    print(f"  - {user.username}: encrypted={user.password_encypted}, algo={user.algorithm}, key={user.key_data}")

# Demander quel utilisateur tester
username = input("\nEntrez le nom d'utilisateur à tester: ").strip()

if not username:
    print("❌ Nom d'utilisateur vide")
    sys.exit(1)

user = CustomUser.objects.filter(username=username).first()

if not user:
    print(f"❌ Utilisateur '{username}' non trouvé")
    sys.exit(1)

print(f"\n2. Utilisateur trouvé: {user.username}")
print(f"   - Password encrypted: {user.password_encypted}")
print(f"   - Algorithm: {user.algorithm}")
print(f"   - Key data: {user.key_data}")

# Vérifier le dictionnaire
print(f"\n3. Vérification du dictionnaire...")
with open('backend/dic.txt', 'r') as f:
    dictionary = [line.strip() for line in f if line.strip()]

print(f"   - Taille: {len(dictionary)} mots")
print(f"   - Contient '122': {'122' in dictionary}")
print(f"   - Premiers mots: {dictionary[:5]}")
print(f"   - Derniers mots: {dictionary[-5:]}")

if '122' not in dictionary:
    print("\n   ⚠️  '122' n'est PAS dans le dictionnaire!")
    print("   Ajout de '122' au dictionnaire...")
    dictionary.append('122')
    with open('backend/dic.txt', 'a') as f:
        f.write('\n122')
    print("   ✅ '122' ajouté!")

# Ajouter l'utilisateur à test_users.txt
test_users_file = 'test_users.txt'
with open(test_users_file, 'r', encoding='utf-8') as f:
    existing = {line.strip() for line in f if line.strip()}

if username not in existing:
    with open(test_users_file, 'a', encoding='utf-8') as f:
        f.write(f'\n{username}')
    print(f"\n4. Utilisateur '{username}' ajouté à test_users.txt")

# Test attaque par dictionnaire
print(f"\n5. Lancement de l'attaque par dictionnaire...")
instruction = {
    "target_username": username,
    "mode": "dictionary",
    "dictionary": dictionary,
    "limit": 0,
    "max_seconds": 60
}

result = run_attack(instruction)

print(f"\n6. RÉSULTATS:")
print(f"   - Status: {'✅ REUSSI' if result.get('matches_count', 0) > 0 else '❌ ECHOUE'}")
print(f"   - Tentatives: {result.get('attempts', 0)}")
print(f"   - Temps: {result.get('time_sec', 0):.6f} secondes")
print(f"   - Matches count: {result.get('matches_count', 0)}")

if result.get('matches_count', 0) > 0:
    print(f"\n✅ MOT DE PASSE TROUVÉ!")
    for i, match in enumerate(result['matches'][:5], 1):
        print(f"\n   Match {i}:")
        print(f"     - Plaintext: {match.get('candidate_plaintext')}")
        print(f"     - Password: {match.get('candidate_key', {}).get('password_candidate')}")
        print(f"     - Confidence: {match.get('confidence')}")
else:
    print(f"\n❌ MOT DE PASSE NON TROUVÉ")
    print(f"\n   Erreurs: {result.get('errors', [])}")
    
    # Debug manuel
    print(f"\n7. TEST MANUEL:")
    from backend.cryptotoolbox.attack.utils import clean_text
    
    # Parser key_data
    key_data = user.key_data
    for _ in range(2):
        if isinstance(key_data, str):
            try:
                key_data = json.loads(key_data)
            except:
                break
    
    print(f"   - Key data parsé: {key_data}")
    
    if user.algorithm.lower() in ['caesar', 'cesar']:
        shift = key_data.get('shift') if isinstance(key_data, dict) else None
        print(f"   - Shift: {shift}")
        
        # Tester avec "122"
        password = "122"
        txt = clean_text(password)
        print(f"   - '122' après clean_text: '{txt}'")
        
        from string import ascii_uppercase
        cipher = ''.join(ascii_uppercase[(ord(ch) - 65 + shift) % 26] for ch in txt)
        print(f"   - '122' chiffré: '{cipher}'")
        print(f"   - Stored encrypted: '{user.password_encypted}'")
        print(f"   - Match: {cipher == user.password_encypted}")

print("\n" + "="*80)
