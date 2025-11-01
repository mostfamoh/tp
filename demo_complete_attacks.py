"""
Script de démonstration complète - Partie 3
Création de 3 utilisateurs avec différents niveaux de complexité et test des attaques

Utilisateurs créés:
1. test_weak_012 - Mot de passe: "012" (charset: {0,1,2})
2. test_medium_123456 - Mot de passe: "123456" (charset: {0-9})
3. test_strong_aB3@x - Mot de passe: "aB3@x" (charset: a-z, A-Z, 0-9, spéciaux)
"""

import sys
import os
import json
import django

# Configuration Django
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox import encrypt_with_algorithm
from backend.cryptotoolbox.attack.attack_runner import run_attack


def print_section(title):
    """Afficher une section formatée"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def create_test_user(username, password, algorithm, key_data, description):
    """Créer un utilisateur de test avec son mot de passe chiffré"""
    print(f"📝 Création de l'utilisateur: {username}")
    print(f"   Mot de passe: {password}")
    print(f"   Description: {description}")
    
    # Supprimer l'utilisateur s'il existe déjà
    CustomUser.objects.filter(username=username).delete()
    
    # Convertir les chiffres en lettres pour le chiffrement
    digit_to_letter = {str(i): chr(ord('A') + i) for i in range(10)}
    password_for_encryption = ''.join(digit_to_letter.get(c, c) for c in password)
    
    print(f"   Conversion pour chiffrement: {password} → {password_for_encryption}")
    
    # Chiffrer le mot de passe
    encrypted = encrypt_with_algorithm(algorithm, password_for_encryption, key_data)
    print(f"   Algorithme: {algorithm}")
    print(f"   Clé: {key_data}")
    print(f"   Mot de passe chiffré: {encrypted}")
    
    # Créer l'utilisateur
    user = CustomUser.objects.create(
        username=username,
        password_encypted=encrypted,
        algorithm=algorithm,
        key_data=json.dumps(key_data)
    )
    
    print(f"✅ Utilisateur créé avec succès!\n")
    return user


def run_brute_force_attack(username, description):
    """Exécuter une attaque par force brute"""
    print(f"\n⚔️  ATTAQUE PAR FORCE BRUTE sur {username}")
    print(f"   {description}\n")
    
    instruction = {
        "target_username": username,
        "mode": "bruteforce",
        "limit": 0,  # Pas de limite
        "max_seconds": 60  # Maximum 60 secondes
    }
    
    result = run_attack(instruction)
    
    if result.get('error'):
        print(f"❌ ERREUR: {result['error']}")
        return result
    
    print(f"📊 RÉSULTATS:")
    print(f"   Algorithme: {result['algorithm']}")
    print(f"   Tentatives: {result['attempts']:,}")
    print(f"   Temps écoulé: {result['time_sec']:.6f} secondes")
    print(f"   Vitesse: {result['attempts']/result['time_sec']:,.0f} tentatives/seconde")
    print(f"   Correspondances trouvées: {result['matches_count']}")
    
    if result['matches_count'] > 0:
        print(f"\n   ✅ MOT DE PASSE TROUVÉ!")
        top_match = result['matches'][0]
        print(f"   Candidat: {top_match['candidate_plaintext']}")
        print(f"   Clé: {top_match['candidate_key']}")
        print(f"   Confiance: {top_match['confidence']}")
        print(f"   Note: {top_match['notes']}")
    else:
        print(f"\n   ❌ Aucun mot de passe trouvé")
    
    if result.get('timeout_reached'):
        print(f"   ⏱️  TIMEOUT: Limite de temps atteinte")
    
    if result.get('limit_reached'):
        print(f"   🛑 LIMITE: Nombre maximum de tentatives atteint")
    
    return result


def run_dictionary_attack(username, dictionary, description):
    """Exécuter une attaque par dictionnaire"""
    print(f"\n📖 ATTAQUE PAR DICTIONNAIRE sur {username}")
    print(f"   {description}")
    print(f"   Taille du dictionnaire: {len(dictionary)} mots\n")
    
    instruction = {
        "target_username": username,
        "mode": "dictionary",
        "dictionary": dictionary
    }
    
    result = run_attack(instruction)
    
    if result.get('error'):
        print(f"❌ ERREUR: {result['error']}")
        return result
    
    print(f"📊 RÉSULTATS:")
    print(f"   Algorithme: {result['algorithm']}")
    print(f"   Tentatives: {result['attempts']:,}")
    print(f"   Temps écoulé: {result['time_sec']:.6f} secondes")
    print(f"   Vitesse: {result['attempts']/result['time_sec']:,.0f} tentatives/seconde")
    print(f"   Correspondances trouvées: {result['matches_count']}")
    
    if result['matches_count'] > 0:
        print(f"\n   ✅ MOT DE PASSE TROUVÉ!")
        top_match = result['matches'][0]
        print(f"   Candidat: {top_match['candidate_plaintext']}")
        print(f"   Clé: {top_match['candidate_key']}")
        print(f"   Confiance: {top_match['confidence']}")
    else:
        print(f"\n   ❌ Aucun mot de passe trouvé")
    
    return result


def generate_dictionary_for_case(case_type):
    """Générer un dictionnaire adapté au type de cas"""
    import itertools
    
    if case_type == 1:
        # Cas 1: 3 caractères {0,1,2}
        charset = "012"
        length = 3
        # Générer toutes les combinaisons possibles
        return [''.join(p) for p in itertools.product(charset, repeat=length)]
    
    elif case_type == 2:
        # Cas 2: 6 chiffres {0-9}
        # Générer un échantillon de mots de passe communs
        common = ["123456", "000000", "111111", "123123", "654321", "012345"]
        # Ajouter quelques combinaisons aléatoires
        import random
        for _ in range(1000):
            pwd = ''.join(random.choice("0123456789") for _ in range(6))
            if pwd not in common:
                common.append(pwd)
        return common
    
    elif case_type == 3:
        # Cas 3: Alphanumérique + spéciaux
        common = ["aB3@x", "Pass123!", "Qwerty1@", "Test@123", "Admin@1"]
        # Ajouter quelques variations
        import random
        import string
        charset = string.ascii_letters + string.digits + "@#$%"
        for _ in range(1000):
            pwd = ''.join(random.choice(charset) for _ in range(5))
            common.append(pwd)
        return common


def main():
    """Fonction principale"""
    print_section("DÉMONSTRATION COMPLÈTE - PARTIE 3")
    print("Ce script crée 3 utilisateurs avec différents niveaux de sécurité")
    print("et teste les attaques par force brute et dictionnaire sur chacun.\n")
    
    # Ajouter les utilisateurs au fichier test_users.txt
    test_users_file = os.path.join(project_root, 'test_users.txt')
    with open(test_users_file, 'r', encoding='utf-8') as f:
        existing_users = {line.strip() for line in f if line.strip()}
    
    new_users = {'test_weak_012', 'test_medium_123456', 'test_strong_aB3@x'}
    
    if not new_users.issubset(existing_users):
        with open(test_users_file, 'a', encoding='utf-8') as f:
            for user in new_users:
                if user not in existing_users:
                    f.write(f"\n{user}")
        print("✅ Utilisateurs ajoutés au fichier test_users.txt\n")
    
    # Stockage des résultats
    all_results = {}
    
    # ==========================================================================
    # CAS 1 : MOT DE PASSE TRÈS FAIBLE
    # ==========================================================================
    print_section("CAS 1 : MOT DE PASSE TRÈS FAIBLE - {0,1,2}")
    
    user1 = create_test_user(
        username="test_weak_012",
        password="012",
        algorithm="caesar",
        key_data={"shift": 3},
        description="3 caractères parmi {0,1,2} - TRÈS FAIBLE"
    )
    
    # Attaque par force brute
    bf_result_1 = run_brute_force_attack(
        "test_weak_012",
        "Force brute sur espace de 27 combinaisons (3^3)"
    )
    
    # Attaque par dictionnaire
    dict_1 = generate_dictionary_for_case(1)
    dict_result_1 = run_dictionary_attack(
        "test_weak_012",
        dict_1,
        "Dictionnaire contenant toutes les combinaisons possibles"
    )
    
    all_results['case1'] = {
        'user': user1.username,
        'password': '012',
        'brute_force': bf_result_1,
        'dictionary': dict_result_1
    }
    
    # ==========================================================================
    # CAS 2 : MOT DE PASSE FAIBLE
    # ==========================================================================
    print_section("CAS 2 : MOT DE PASSE FAIBLE - {0-9}")
    
    user2 = create_test_user(
        username="test_medium_123456",
        password="123456",
        algorithm="caesar",
        key_data={"shift": 5},
        description="6 chiffres (0-9) - FAIBLE"
    )
    
    # Attaque par force brute (limitée)
    bf_result_2 = run_brute_force_attack(
        "test_medium_123456",
        "Force brute sur espace de 1,000,000 combinaisons (10^6)"
    )
    
    # Attaque par dictionnaire
    dict_2 = generate_dictionary_for_case(2)
    dict_result_2 = run_dictionary_attack(
        "test_medium_123456",
        dict_2,
        "Dictionnaire avec mots de passe communs"
    )
    
    all_results['case2'] = {
        'user': user2.username,
        'password': '123456',
        'brute_force': bf_result_2,
        'dictionary': dict_result_2
    }
    
    # ==========================================================================
    # CAS 3 : MOT DE PASSE MOYEN
    # ==========================================================================
    print_section("CAS 3 : MOT DE PASSE MOYEN - Alphanumérique + Spéciaux")
    
    user3 = create_test_user(
        username="test_strong_aB3@x",
        password="aB3@x",
        algorithm="caesar",
        key_data={"shift": 7},
        description="5 caractères avec majuscules, minuscules, chiffres et spéciaux - MOYEN"
    )
    
    # Attaque par force brute (très limitée, espace trop grand)
    bf_result_3 = run_brute_force_attack(
        "test_strong_aB3@x",
        "Force brute limitée (espace > 7 milliards de combinaisons)"
    )
    
    # Attaque par dictionnaire
    dict_3 = generate_dictionary_for_case(3)
    dict_result_3 = run_dictionary_attack(
        "test_strong_aB3@x",
        dict_3,
        "Dictionnaire avec variations de mots de passe"
    )
    
    all_results['case3'] = {
        'user': user3.username,
        'password': 'aB3@x',
        'brute_force': bf_result_3,
        'dictionary': dict_result_3
    }
    
    # ==========================================================================
    # RÉSUMÉ FINAL
    # ==========================================================================
    print_section("RÉSUMÉ COMPARATIF DES ATTAQUES")
    
    print("┌────────────────────┬──────────────┬──────────────┬──────────────────┐")
    print("│ Utilisateur        │ Mot de passe │ Force Brute  │ Dictionnaire     │")
    print("├────────────────────┼──────────────┼──────────────┼──────────────────┤")
    
    for case_id, data in all_results.items():
        bf = data['brute_force']
        di = data['dictionary']
        bf_status = "✅ TROUVÉ" if bf.get('matches_count', 0) > 0 else "❌ ÉCHEC"
        di_status = "✅ TROUVÉ" if di.get('matches_count', 0) > 0 else "❌ ÉCHEC"
        
        print(f"│ {data['user']:<18} │ {data['password']:<12} │ {bf_status:<12} │ {di_status:<16} │")
    
    print("└────────────────────┴──────────────┴──────────────┴──────────────────┘")
    
    print("\n📊 STATISTIQUES DÉTAILLÉES:\n")
    
    for case_id, data in all_results.items():
        case_num = case_id[-1]
        print(f"CAS {case_num} - {data['user']}:")
        print(f"  Mot de passe: {data['password']}")
        
        bf = data['brute_force']
        if not bf.get('error'):
            print(f"  Force Brute:")
            print(f"    - Tentatives: {bf['attempts']:,}")
            print(f"    - Temps: {bf['time_sec']:.6f} secondes")
            print(f"    - Résultat: {'✅ TROUVÉ' if bf.get('matches_count', 0) > 0 else '❌ ÉCHEC'}")
        
        di = data['dictionary']
        if not di.get('error'):
            print(f"  Dictionnaire:")
            print(f"    - Tentatives: {di['attempts']:,}")
            print(f"    - Temps: {di['time_sec']:.6f} secondes")
            print(f"    - Résultat: {'✅ TROUVÉ' if di.get('matches_count', 0) > 0 else '❌ ÉCHEC'}")
        print()
    
    # Sauvegarder les résultats
    output_file = os.path.join(project_root, 'demo_attack_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Résultats complets sauvegardés dans: {output_file}")
    
    print_section("CONCLUSIONS")
    print("1. CAS 1 (012) : Espace de 27 combinaisons")
    print("   → Craqué INSTANTANÉMENT par force brute")
    print("   → ❌ EXTRÊMEMENT DANGEREUX\n")
    
    print("2. CAS 2 (123456) : Espace de 1 million de combinaisons")
    print("   → Craqué en quelques millisecondes par force brute")
    print("   → ❌ TRÈS DANGEREUX\n")
    
    print("3. CAS 3 (aB3@x) : Espace > 7 milliards de combinaisons")
    print("   → Force brute limitée par le temps")
    print("   → Peut être trouvé par dictionnaire si le mot est commun")
    print("   → ⚠️  MOYEN (mais insuffisant pour données sensibles)\n")
    
    print("💡 RECOMMANDATION:")
    print("   Utilisez des mots de passe de 12+ caractères avec:")
    print("   - Majuscules + minuscules + chiffres + caractères spéciaux")
    print("   - Hachage fort (Argon2id)")
    print("   - Rate limiting (5 tentatives / 15 minutes)")
    print("   - Authentification multi-facteurs (MFA)")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
