#!/usr/bin/env python
"""
Test de l'interaction entre la protection et les attaques
"""

import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000/api'

def create_test_user(username='test_attack_protection', password='123'):
    """Crée un utilisateur de test"""
    url = f'{BASE_URL}/regester/'
    data = {
        'username': username,
        'password': password,
        'algorithm': 'caesar',
        'key_param': {'shift': 3}
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code in [200, 201]:
            print(f"✅ Utilisateur '{username}' créé")
            return True
        elif response.status_code == 409:
            print(f"ℹ️  Utilisateur '{username}' existe déjà")
            return True
        else:
            print(f"❌ Erreur création: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def activate_protection(username):
    """Active la protection pour un utilisateur"""
    url = f'{BASE_URL}/users/{username}/toggle-protection/'
    data = {'enabled': True}
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"✅ Protection activée pour '{username}'")
            return True
        else:
            print(f"❌ Erreur activation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def get_protection_status(username):
    """Récupère le statut de protection"""
    url = f'{BASE_URL}/users/{username}/protection-status/'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def run_dictionary_attack(username, dictionary_type='dict_012'):
    """Lance une attaque par dictionnaire"""
    url = f'{BASE_URL}/attack/full_dictionary/'
    data = {
        'target_username': username,
        'max_seconds': 120,
        'limit': 0,
        'dictionary_type': dictionary_type
    }
    
    print(f"\n🎯 Lancement d'une attaque par dictionnaire ({dictionary_type})...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=data)
        elapsed = time.time() - start_time
        
        print(f"   Temps écoulé: {elapsed:.2f}s")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Résultat: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        else:
            print(f"   Erreur: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def run_bruteforce_attack(username, max_seconds=30):
    """Lance une attaque par force brute"""
    url = f'{BASE_URL}/attack/full_bruteforce/'
    data = {
        'target_username': username,
        'max_seconds': max_seconds,
        'limit': 1000
    }
    
    print(f"\n💪 Lancement d'une attaque par force brute...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=data)
        elapsed = time.time() - start_time
        
        print(f"   Temps écoulé: {elapsed:.2f}s")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Résultat: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        else:
            print(f"   Erreur: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    print("=" * 80)
    print("  🧪 TEST: PROTECTION vs ATTAQUES PAR DICTIONNAIRE/FORCE BRUTE")
    print("=" * 80 + "\n")
    
    username = 'test_attack_protection'
    
    # Étape 1: Créer l'utilisateur
    print("📝 ÉTAPE 1: Création de l'utilisateur")
    create_test_user(username, '123')  # Mot de passe: 123 → BCD → chiffré
    
    # Étape 2: Vérifier le statut initial
    print("\n📊 ÉTAPE 2: Statut initial")
    status = get_protection_status(username)
    if status:
        print(f"   Protection: {status['protection_enabled']}")
        print(f"   Tentatives échouées: {status['failed_attempts']}/3")
        print(f"   Verrouillé: {status['is_locked']}")
    
    # Étape 3: Test d'attaque SANS protection
    print("\n" + "─" * 80)
    print("🔓 ÉTAPE 3: Attaque SANS protection")
    print("─" * 80)
    
    result = run_dictionary_attack(username, 'dict_012')
    if result:
        if result.get('found'):
            print(f"   ✅ Mot de passe trouvé: {result.get('plaintext')}")
            print(f"   Tentatives: {result.get('attempts')}")
            print(f"   Temps: {result.get('time_seconds')}s")
        else:
            print(f"   ❌ Mot de passe NON trouvé")
    
    status = get_protection_status(username)
    if status:
        print(f"\n   Statut après attaque:")
        print(f"   • Tentatives échouées: {status['failed_attempts']}/3")
        print(f"   • Verrouillé: {status['is_locked']}")
    
    # Étape 4: Activer la protection
    print("\n" + "─" * 80)
    print("🛡️  ÉTAPE 4: Activation de la protection")
    print("─" * 80)
    
    activate_protection(username)
    status = get_protection_status(username)
    if status:
        print(f"   Protection: {status['protection_enabled']}")
    
    # Étape 5: Test d'attaque AVEC protection
    print("\n" + "─" * 80)
    print("🔐 ÉTAPE 5: Attaque AVEC protection")
    print("─" * 80)
    print("⚠️  QUESTION: L'attaque va-t-elle être bloquée ?")
    
    result = run_dictionary_attack(username, 'dict_012')
    if result:
        if result.get('found'):
            print(f"\n   ⚠️  Le mot de passe a été trouvé!")
            print(f"   • Tentatives: {result.get('attempts')}")
            print(f"   • Temps: {result.get('time_seconds')}s")
        else:
            print(f"\n   ❌ Mot de passe NON trouvé")
    
    status = get_protection_status(username)
    if status:
        print(f"\n   Statut après attaque:")
        print(f"   • Protection: {status['protection_enabled']}")
        print(f"   • Tentatives échouées: {status['failed_attempts']}/3")
        print(f"   • Verrouillé: {status['is_locked']}")
    
    # Étape 6: Test de force brute
    print("\n" + "─" * 80)
    print("💪 ÉTAPE 6: Attaque par force brute AVEC protection")
    print("─" * 80)
    
    result = run_bruteforce_attack(username, max_seconds=10)
    
    status = get_protection_status(username)
    if status:
        print(f"\n   Statut après force brute:")
        print(f"   • Tentatives échouées: {status['failed_attempts']}/3")
        print(f"   • Verrouillé: {status['is_locked']}")
    
    # Conclusion
    print("\n" + "=" * 80)
    print("  📊 ANALYSE DES RÉSULTATS")
    print("=" * 80)
    
    print("\n❓ QUESTION IMPORTANTE:")
    print("   La protection s'applique-t-elle aux attaques automatiques ?")
    
    print("\n🔍 OBSERVATION:")
    print("   Les attaques par dictionnaire/force brute utilisent les endpoints")
    print("   d'attaque (/attack/full_dictionary/ et /attack/full_bruteforce/)")
    print("   qui NE passent PAS par l'endpoint de login (/login/).")
    
    print("\n⚠️  PROBLÈME POTENTIEL:")
    print("   Si les attaques ne passent pas par login_user(), elles ne sont")
    print("   PAS affectées par la protection ! Elles déchiffrent directement.")
    
    print("\n💡 SOLUTION POSSIBLE:")
    print("   1. Faire passer les attaques par l'endpoint de login")
    print("   2. OU ajouter une vérification de protection dans les endpoints d'attaque")
    print("   3. OU limiter le nombre d'attaques par IP/compte")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    main()
