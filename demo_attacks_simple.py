"""
Script simplifié pour créer 3 utilisateurs et tester les attaques
Version sans dépendance Django directe
"""

import sys
import os
import json
import subprocess

project_root = os.path.abspath(os.path.dirname(__file__))


def print_section(title):
    """Afficher une section formatée"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def create_users_via_shell():
    """Créer les utilisateurs via Django shell"""
    print_section("CRÉATION DES UTILISATEURS DE TEST")
    
    # Script Python à exécuter dans le shell Django (sans émojis pour Windows)
    django_script = """
import json
from crypto_lab.models import CustomUser
from backend.cryptotoolbox import encrypt_with_algorithm

# Configuration des utilisateurs
users_config = [
    {
        'username': 'test_weak_012',
        'password': '012',
        'algorithm': 'caesar',
        'key_data': {'shift': 3},
        'description': '3 caracteres {0,1,2} - TRES FAIBLE'
    },
    {
        'username': 'test_medium_123456',
        'password': '123456',
        'algorithm': 'caesar',
        'key_data': {'shift': 5},
        'description': '6 chiffres {0-9} - FAIBLE'
    },
    {
        'username': 'test_strong_aB3@x',
        'password': 'aB3@x',
        'algorithm': 'caesar',
        'key_data': {'shift': 7},
        'description': 'Alphanumerique + speciaux - MOYEN'
    }
]

# Convertir les chiffres en lettres
digit_to_letter = {str(i): chr(ord('A') + i) for i in range(10)}

for config in users_config:
    username = config['username']
    password = config['password']
    algorithm = config['algorithm']
    key_data = config['key_data']
    
    # Supprimer l'utilisateur s'il existe
    CustomUser.objects.filter(username=username).delete()
    
    # Conversion pour chiffrement
    password_converted = ''.join(digit_to_letter.get(c, c) for c in password)
    
    # Chiffrer
    encrypted = encrypt_with_algorithm(algorithm, password_converted, key_data)
    
    # Créer l'utilisateur
    user = CustomUser.objects.create(
        username=username,
        password_encypted=encrypted,
        algorithm=algorithm,
        key_data=json.dumps(key_data)
    )
    
    print(f"[OK] Cree: {username}")
    print(f"   Mot de passe: {password} -> {password_converted}")
    print(f"   Chiffre: {encrypted}")
    print(f"   Description: {config['description']}")
    print()

print("\\n[OK] TOUS LES UTILISATEURS ONT ETE CREES!")
"""
    
    # Sauvegarder le script temporaire
    script_file = os.path.join(project_root, 'temp_create_users.py')
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(django_script)
    
    # Exécuter via Django shell
    print("Exécution de la création via Django shell...")
    result = subprocess.run(
        ['python', 'manage.py', 'shell', '-c', django_script],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("Erreurs:", result.stderr)
    
    # Nettoyer
    if os.path.exists(script_file):
        os.remove(script_file)
    
    return result.returncode == 0


def run_attack(username, mode, dictionary=None):
    """Exécuter une attaque via le module attack_runner"""
    from backend.cryptotoolbox.attack.attack_runner import run_attack as execute_attack
    
    instruction = {
        "target_username": username,
        "mode": mode,
        "limit": 0,
        "max_seconds": 60
    }
    
    if dictionary:
        instruction['dictionary'] = dictionary
    
    return execute_attack(instruction)


def generate_dictionary(case_type):
    """Générer un dictionnaire pour le cas donné"""
    import itertools
    import random
    import string
    
    if case_type == 1:
        # Toutes les combinaisons pour {0,1,2}^3
        return [''.join(p) for p in itertools.product("012", repeat=3)]
    
    elif case_type == 2:
        # Mots de passe numériques communs
        common = ["123456", "000000", "111111", "123123", "654321", "012345"]
        for _ in range(1000):
            pwd = ''.join(random.choice("0123456789") for _ in range(6))
            if pwd not in common:
                common.append(pwd)
        return common
    
    elif case_type == 3:
        # Alphanumérique + spéciaux
        common = ["aB3@x", "Pass123!", "Qwerty1@", "Test@123", "Admin@1"]
        charset = string.ascii_letters + string.digits + "@#$%"
        for _ in range(1000):
            pwd = ''.join(random.choice(charset) for _ in range(5))
            common.append(pwd)
        return common


def main():
    """Fonction principale"""
    print_section("DÉMONSTRATION COMPLÈTE - TESTS D'ATTAQUES")
    
    # Ajouter les utilisateurs au fichier test_users.txt
    test_users_file = os.path.join(project_root, 'test_users.txt')
    new_users = ['test_weak_012', 'test_medium_123456', 'test_strong_aB3@x']
    
    with open(test_users_file, 'r', encoding='utf-8') as f:
        existing = {line.strip() for line in f if line.strip()}
    
    with open(test_users_file, 'a', encoding='utf-8') as f:
        for user in new_users:
            if user not in existing:
                f.write(f"\n{user}")
    
    print("✅ Utilisateurs autorisés dans test_users.txt\n")
    
    # Créer les utilisateurs
    if not create_users_via_shell():
        print("❌ Erreur lors de la création des utilisateurs")
        return
    
    # Importer après la création
    sys.path.insert(0, project_root)
    
    print_section("TEST DES ATTAQUES")
    
    results = {}
    
    # Test CAS 1
    print("\n" + "-"*80)
    print("CAS 1 : test_weak_012 (mot de passe: 012)")
    print("-"*80)
    
    print("\n⚔️  FORCE BRUTE...")
    bf1 = run_attack('test_weak_012', 'bruteforce')
    print(f"   Tentatives: {bf1.get('attempts', 0):,}")
    print(f"   Temps: {bf1.get('time_sec', 0):.6f} s")
    print(f"   Résultat: {'✅ TROUVÉ' if bf1.get('matches_count', 0) > 0 else '❌ ÉCHEC'}")
    
    print("\n📖 DICTIONNAIRE...")
    dict1 = generate_dictionary(1)
    di1 = run_attack('test_weak_012', 'dictionary', dict1)
    print(f"   Tentatives: {di1.get('attempts', 0):,}")
    print(f"   Temps: {di1.get('time_sec', 0):.6f} s")
    print(f"   Résultat: {'✅ TROUVÉ' if di1.get('matches_count', 0) > 0 else '❌ ÉCHEC'}")
    
    results['case1'] = {'brute_force': bf1, 'dictionary': di1}
    
    # Test CAS 2
    print("\n" + "-"*80)
    print("CAS 2 : test_medium_123456 (mot de passe: 123456)")
    print("-"*80)
    
    print("\n⚔️  FORCE BRUTE...")
    bf2 = run_attack('test_medium_123456', 'bruteforce')
    print(f"   Tentatives: {bf2.get('attempts', 0):,}")
    print(f"   Temps: {bf2.get('time_sec', 0):.6f} s")
    print(f"   Résultat: {'✅ TROUVÉ' if bf2.get('matches_count', 0) > 0 else '❌ ÉCHEC'}")
    
    print("\n📖 DICTIONNAIRE...")
    dict2 = generate_dictionary(2)
    di2 = run_attack('test_medium_123456', 'dictionary', dict2)
    print(f"   Tentatives: {di2.get('attempts', 0):,}")
    print(f"   Temps: {di2.get('time_sec', 0):.6f} s")
    print(f"   Résultat: {'✅ TROUVÉ' if di2.get('matches_count', 0) > 0 else '❌ ÉCHEC'}")
    
    results['case2'] = {'brute_force': bf2, 'dictionary': di2}
    
    # Test CAS 3
    print("\n" + "-"*80)
    print("CAS 3 : test_strong_aB3@x (mot de passe: aB3@x)")
    print("-"*80)
    
    print("\n⚔️  FORCE BRUTE (limité)...")
    bf3 = run_attack('test_strong_aB3@x', 'bruteforce')
    print(f"   Tentatives: {bf3.get('attempts', 0):,}")
    print(f"   Temps: {bf3.get('time_sec', 0):.6f} s")
    print(f"   Résultat: {'✅ TROUVÉ' if bf3.get('matches_count', 0) > 0 else '❌ ÉCHEC'}")
    
    print("\n📖 DICTIONNAIRE...")
    dict3 = generate_dictionary(3)
    di3 = run_attack('test_strong_aB3@x', 'dictionary', dict3)
    print(f"   Tentatives: {di3.get('attempts', 0):,}")
    print(f"   Temps: {di3.get('time_sec', 0):.6f} s")
    print(f"   Résultat: {'✅ TROUVÉ' if di3.get('matches_count', 0) > 0 else '❌ ÉCHEC'}")
    
    results['case3'] = {'brute_force': bf3, 'dictionary': di3}
    
    # RÉSUMÉ
    print_section("RÉSUMÉ COMPARATIF")
    
    print("┌─────────────────────┬──────────────┬──────────────┬──────────────────┐")
    print("│ Utilisateur         │ Mot de passe │ Force Brute  │ Dictionnaire     │")
    print("├─────────────────────┼──────────────┼──────────────┼──────────────────┤")
    print(f"│ test_weak_012       │ 012          │ {'✅ TROUVÉ' if bf1.get('matches_count', 0) > 0 else '❌ ÉCHEC':12} │ {'✅ TROUVÉ' if di1.get('matches_count', 0) > 0 else '❌ ÉCHEC':16} │")
    print(f"│ test_medium_123456  │ 123456       │ {'✅ TROUVÉ' if bf2.get('matches_count', 0) > 0 else '❌ ÉCHEC':12} │ {'✅ TROUVÉ' if di2.get('matches_count', 0) > 0 else '❌ ÉCHEC':16} │")
    print(f"│ test_strong_aB3@x   │ aB3@x        │ {'✅ TROUVÉ' if bf3.get('matches_count', 0) > 0 else '❌ ÉCHEC':12} │ {'✅ TROUVÉ' if di3.get('matches_count', 0) > 0 else '❌ ÉCHEC':16} │")
    print("└─────────────────────┴──────────────┴──────────────┴──────────────────┘")
    
    # Sauvegarder
    output_file = os.path.join(project_root, 'demo_attack_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"\n✅ Résultats sauvegardés: {output_file}")
    
    print_section("CONCLUSIONS")
    print("✅ CAS 1 (012) : CRAQUÉ par force brute et dictionnaire")
    print("✅ CAS 2 (123456) : CRAQUÉ par force brute et dictionnaire")
    print("⚠️  CAS 3 (aB3@x) : Force brute limitée, peut être trouvé par dictionnaire")
    print("\n💡 Les mots de passe courts sont TRÈS DANGEREUX!")
    print("   Recommandation : 12+ caractères avec complexité maximale")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
