"""
PARTIE 3 : Démonstration des attaques selon la complexité du mot de passe
Objectif : Montrer que les attaques réussissent sur les mots de passe simples
           mais échouent sur les mots de passe complexes
"""

import os
import sys
import django
import json
import time
import itertools

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox import encrypt_with_algorithm


def print_section(title):
    """Afficher une section formatée"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def create_test_user(username, password, description):
    """Créer un utilisateur de test"""
    # Supprimer s'il existe
    CustomUser.objects.filter(username=username).delete()
    
    # Convertir les chiffres en lettres pour le chiffrement
    digit_to_letter = {str(i): chr(ord('A') + i) for i in range(10)}
    password_converted = ''.join(digit_to_letter.get(c, c) for c in password)
    
    # Chiffrer avec César (shift=3 pour tous)
    algorithm = "caesar"
    shift = 3
    encrypted = encrypt_with_algorithm(algorithm, password_converted, {"shift": shift})
    
    # Créer l'utilisateur
    user = CustomUser.objects.create(
        username=username,
        password_encypted=encrypted,
        algorithm=algorithm,
        key_data=json.dumps({"shift": shift})
    )
    
    print(f"[OK] Utilisateur créé: {username}")
    print(f"     Description: {description}")
    print(f"     Mot de passe: {password}")
    print(f"     Converti en: {password_converted}")
    print(f"     Chiffré: {encrypted}")
    print()
    
    return user, password_converted, encrypted


def attaque_force_brute(password_chiffre, charset, length, max_attempts=100000):
    """
    Attaque par force brute
    Essaie toutes les combinaisons possibles du charset
    """
    print(f"   Charset: {charset}")
    print(f"   Longueur: {length} caractères")
    
    # Calculer le nombre total de combinaisons
    total_combinations = len(charset) ** length
    print(f"   Combinaisons totales: {total_combinations:,}")
    
    # Limiter les tentatives pour ne pas bloquer
    attempts = min(total_combinations, max_attempts)
    print(f"   Tentatives max: {attempts:,}")
    
    # Conversion chiffres → lettres
    digit_to_letter = {str(i): chr(ord('A') + i) for i in range(10)}
    
    start_time = time.time()
    
    # Essayer toutes les combinaisons
    for i, combination in enumerate(itertools.product(charset, repeat=length)):
        if i >= attempts:
            print(f"\n   [LIMITE] Arrêt après {attempts:,} tentatives")
            break
        
        # Générer le mot de passe candidat
        candidate = ''.join(combination)
        
        # Convertir en lettres
        candidate_converted = ''.join(digit_to_letter.get(c, c) for c in candidate)
        
        # Chiffrer avec shift=3
        try:
            encrypted = encrypt_with_algorithm("caesar", candidate_converted, {"shift": 3})
            
            # Comparer
            if encrypted == password_chiffre:
                elapsed = time.time() - start_time
                print(f"\n   [TROUVE] Mot de passe: {candidate}")
                print(f"   Tentatives: {i + 1:,}")
                print(f"   Temps: {elapsed:.6f} secondes")
                return {
                    "success": True,
                    "password": candidate,
                    "attempts": i + 1,
                    "time_seconds": elapsed,
                    "total_possible": total_combinations
                }
        except:
            pass
        
        # Afficher progression tous les 10000
        if (i + 1) % 10000 == 0:
            elapsed = time.time() - start_time
            print(f"   Tentatives: {i + 1:,} / {attempts:,} ({elapsed:.2f}s)")
    
    elapsed = time.time() - start_time
    print(f"\n   [ECHEC] Mot de passe non trouvé")
    print(f"   Tentatives: {attempts:,}")
    print(f"   Temps: {elapsed:.6f} secondes")
    
    return {
        "success": False,
        "attempts": attempts,
        "time_seconds": elapsed,
        "total_possible": total_combinations
    }


def attaque_dictionnaire(password_chiffre, dictionary):
    """
    Attaque par dictionnaire
    Essaie tous les mots du dictionnaire
    """
    print(f"   Taille du dictionnaire: {len(dictionary)} mots")
    
    # Conversion chiffres → lettres
    digit_to_letter = {str(i): chr(ord('A') + i) for i in range(10)}
    
    start_time = time.time()
    
    for i, word in enumerate(dictionary):
        # Convertir en lettres
        word_converted = ''.join(digit_to_letter.get(c, c) for c in word)
        
        # Chiffrer avec shift=3
        try:
            encrypted = encrypt_with_algorithm("caesar", word_converted, {"shift": 3})
            
            # Comparer
            if encrypted == password_chiffre:
                elapsed = time.time() - start_time
                print(f"\n   [TROUVE] Mot de passe: {word}")
                print(f"   Position dans le dictionnaire: {i + 1}")
                print(f"   Temps: {elapsed:.6f} secondes")
                return {
                    "success": True,
                    "password": word,
                    "attempts": i + 1,
                    "time_seconds": elapsed
                }
        except:
            pass
    
    elapsed = time.time() - start_time
    print(f"\n   [ECHEC] Mot de passe non trouvé dans le dictionnaire")
    print(f"   Temps: {elapsed:.6f} secondes")
    
    return {
        "success": False,
        "attempts": len(dictionary),
        "time_seconds": elapsed
    }


def generate_dictionary(case):
    """Générer un dictionnaire adapté à chaque cas"""
    if case == 1:
        # Cas 1: Toutes les combinaisons {0,1,2}^3
        return [''.join(p) for p in itertools.product('012', repeat=3)]
    
    elif case == 2:
        # Cas 2: Mots de passe numériques courants + aléatoires
        common = [
            '000000', '111111', '222222', '333333', '444444',
            '555555', '666666', '777777', '888888', '999999',
            '123456', '654321', '000001', '123123', '456456',
            '012345', '123450', '111222', '222333', '333444'
        ]
        # Ajouter quelques combinaisons séquentielles
        for i in range(0, 1000, 10):
            common.append(str(i).zfill(6))
        return common
    
    elif case == 3:
        # Cas 3: Mots de passe courants + combinaisons simples
        import string
        common = [
            'password', 'Password', 'PASSWORD',
            'admin', 'Admin', 'ADMIN',
            'test123', 'Test123', 'TEST123',
            'password123', 'Password123',
            'qwerty', 'Qwerty', 'QWERTY',
            'abc123', 'Abc123', 'ABC123',
            'pass123', 'Pass123'
        ]
        return common


def main():
    """Fonction principale"""
    print_section("PARTIE 3 : DEMONSTRATION DES ATTAQUES SUR MOTS DE PASSE")
    
    print("Objectif:")
    print("  - Montrer que les mots de passe SIMPLES sont VULNERABLES")
    print("  - Montrer que les mots de passe COMPLEXES sont RESISTANTS")
    print()
    
    # Autoriser les utilisateurs de test
    test_users_file = 'test_users.txt'
    test_usernames = ['cas1_012', 'cas2_123456', 'cas3_complex']
    
    with open(test_users_file, 'r', encoding='utf-8') as f:
        existing = {line.strip() for line in f if line.strip()}
    
    with open(test_users_file, 'a', encoding='utf-8') as f:
        for username in test_usernames:
            if username not in existing:
                f.write(f"\n{username}")
    
    results = {}
    
    # ========================================================================
    # CAS 1 : Mot de passe de 3 caractères {0, 1, 2}
    # ========================================================================
    print_section("CAS 1 : Mot de passe de 3 caractères avec charset {0, 1, 2}")
    
    password1 = "012"
    user1, pwd1_conv, enc1 = create_test_user(
        'cas1_012',
        password1,
        'Mot de passe TRES FAIBLE (3 caractères, 3 valeurs possibles)'
    )
    
    print("▶ ATTAQUE PAR FORCE BRUTE")
    print("-" * 80)
    result1_bf = attaque_force_brute(enc1, '012', 3, max_attempts=100)
    
    print("\n▶ ATTAQUE PAR DICTIONNAIRE")
    print("-" * 80)
    dict1 = generate_dictionary(1)
    result1_dict = attaque_dictionnaire(enc1, dict1)
    
    results['cas1'] = {
        'password': password1,
        'description': '3 caractères {0,1,2}',
        'total_combinations': 3**3,
        'brute_force': result1_bf,
        'dictionary': result1_dict
    }
    
    # ========================================================================
    # CAS 2 : Mot de passe de 6 caractères {0..9}
    # ========================================================================
    print_section("CAS 2 : Mot de passe de 6 caractères avec charset {0..9}")
    
    password2 = "123456"
    user2, pwd2_conv, enc2 = create_test_user(
        'cas2_123456',
        password2,
        'Mot de passe FAIBLE (6 chiffres)'
    )
    
    print("▶ ATTAQUE PAR FORCE BRUTE (limité à 100,000 tentatives)")
    print("-" * 80)
    result2_bf = attaque_force_brute(enc2, '0123456789', 6, max_attempts=100000)
    
    print("\n▶ ATTAQUE PAR DICTIONNAIRE")
    print("-" * 80)
    dict2 = generate_dictionary(2)
    result2_dict = attaque_dictionnaire(enc2, dict2)
    
    results['cas2'] = {
        'password': password2,
        'description': '6 caractères {0-9}',
        'total_combinations': 10**6,
        'brute_force': result2_bf,
        'dictionary': result2_dict
    }
    
    # ========================================================================
    # CAS 3 : Mot de passe complexe
    # ========================================================================
    print_section("CAS 3 : Mot de passe de 6 caractères avec charset complexe")
    
    password3 = "aB3@x9"  # Alphanumérique + spéciaux
    user3, pwd3_conv, enc3 = create_test_user(
        'cas3_complex',
        password3,
        'Mot de passe FORT (6 caractères, charset complet)'
    )
    
    print("▶ ATTAQUE PAR FORCE BRUTE (limité à 10,000 tentatives)")
    print("-" * 80)
    # Charset: a-z, A-Z, 0-9, @#$%&*
    charset3 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*'
    result3_bf = attaque_force_brute(enc3, charset3, 6, max_attempts=10000)
    
    print("\n▶ ATTAQUE PAR DICTIONNAIRE")
    print("-" * 80)
    dict3 = generate_dictionary(3)
    result3_dict = attaque_dictionnaire(enc3, dict3)
    
    results['cas3'] = {
        'password': password3,
        'description': '6 caractères {a-z,A-Z,0-9,spéciaux}',
        'total_combinations': len(charset3)**6,
        'brute_force': result3_bf,
        'dictionary': result3_dict
    }
    
    # ========================================================================
    # TABLEAU RÉCAPITULATIF
    # ========================================================================
    print_section("TABLEAU RECAPITULATIF DES RESULTATS")
    
    print("┌─────────┬──────────────┬─────────────────┬─────────────┬─────────────┐")
    print("│   CAS   │ Mot de passe │   Description   │ Force Brute │ Dictionnaire│")
    print("├─────────┼──────────────┼─────────────────┼─────────────┼─────────────┤")
    
    for cas_name, cas_data in results.items():
        pwd = cas_data['password']
        desc = cas_data['description'][:15]
        bf_status = "✅ TROUVE" if cas_data['brute_force']['success'] else "❌ ECHEC"
        dict_status = "✅ TROUVE" if cas_data['dictionary']['success'] else "❌ ECHEC"
        
        print(f"│ {cas_name:7} │ {pwd:12} │ {desc:15} │ {bf_status:11} │ {dict_status:11} │")
    
    print("└─────────┴──────────────┴─────────────────┴─────────────┴─────────────┘")
    
    # ========================================================================
    # STATISTIQUES DETAILLEES
    # ========================================================================
    print_section("STATISTIQUES DETAILLEES")
    
    for cas_name, cas_data in results.items():
        print(f"\n{cas_name.upper()} : {cas_data['password']}")
        print(f"  Description: {cas_data['description']}")
        print(f"  Combinaisons possibles: {cas_data['total_combinations']:,}")
        print(f"\n  Force Brute:")
        print(f"    - Résultat: {'✅ REUSSI' if cas_data['brute_force']['success'] else '❌ ECHOUE'}")
        print(f"    - Tentatives: {cas_data['brute_force']['attempts']:,}")
        print(f"    - Temps: {cas_data['brute_force']['time_seconds']:.6f} secondes")
        print(f"\n  Dictionnaire:")
        print(f"    - Résultat: {'✅ REUSSI' if cas_data['dictionary']['success'] else '❌ ECHOUE'}")
        print(f"    - Tentatives: {cas_data['dictionary']['attempts']:,}")
        print(f"    - Temps: {cas_data['dictionary']['time_seconds']:.6f} secondes")
    
    # ========================================================================
    # CONCLUSIONS ET RECOMMANDATIONS
    # ========================================================================
    print_section("CONCLUSIONS")
    
    print("📊 OBSERVATIONS:")
    print()
    print("1. CAS 1 (012) - 3 caractères {0,1,2}")
    print("   ✅ Combinaisons: 27 (3³)")
    print("   ✅ Résultat: CRAQUE en quelques millisecondes")
    print("   💡 Verdict: EXTREMEMENT VULNERABLE")
    print()
    print("2. CAS 2 (123456) - 6 chiffres {0-9}")
    print("   ✅ Combinaisons: 1,000,000 (10⁶)")
    print("   ✅ Résultat: CRAQUE rapidement (dictionnaire)")
    print("   💡 Verdict: TRES VULNERABLE")
    print()
    print("3. CAS 3 (aB3@x9) - 6 caractères complexes")
    print(f"   ❌ Combinaisons: {len('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*')**6:,} (68⁶)")
    print("   ❌ Résultat: RESISTE aux attaques simples")
    print("   💡 Verdict: RESISTANT (mais 8+ caractères recommandés)")
    
    print_section("RECOMMANDATIONS DE PROTECTION")
    
    print("""
🔐 MESURES DE PROTECTION RECOMMANDEES:

1. LONGUEUR DU MOT DE PASSE
   ✅ Minimum : 12 caractères
   ✅ Recommandé : 16+ caractères
   ❌ A éviter : Moins de 8 caractères

2. COMPLEXITE
   ✅ Majuscules + minuscules + chiffres + caractères spéciaux
   ✅ Pas de mots du dictionnaire
   ❌ Pas de séquences (123456, abcdef)
   ❌ Pas de patterns prévisibles

3. HACHAGE SECURISE
   ✅ Utiliser Argon2id (recommandé)
   ✅ Alternative: bcrypt ou PBKDF2
   ✅ Avec un salt unique par utilisateur
   ❌ NE JAMAIS utiliser MD5 ou SHA1 seuls

4. MESURES ADDITIONNELLES
   ✅ Rate limiting (limiter les tentatives)
   ✅ Authentification à deux facteurs (2FA/MFA)
   ✅ Détection des tentatives d'attaque
   ✅ Blocage temporaire après X échecs
   ✅ CAPTCHA après plusieurs tentatives

5. ALGORITHME CESAR
   ❌ NE JAMAIS utiliser en production
   ❌ Seulement 26 clés possibles
   ✅ OK pour l'enseignement et la démonstration
""")
    
    # Sauvegarder les résultats
    os.makedirs('docs/results', exist_ok=True)
    with open('docs/results/partie3_resultats.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés dans: docs/results/partie3_resultats.json")
    
    print_section("DEMONSTRATION TERMINEE")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
