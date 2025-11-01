#!/usr/bin/env python
"""
Test de protection avec un utilisateur existant
"""

import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000/api'

def main():
    print("=" * 80)
    print("  🧪 TEST: PROTECTION vs ATTAQUES")
    print("=" * 80 + "\n")
    
    username = 'bellia'  # Utilisateur existant
    
    # Étape 1: Désactiver la protection d'abord
    print("📝 ÉTAPE 1: Désactivation de la protection")
    response = requests.post(f'{BASE_URL}/users/{username}/toggle-protection/', 
                            json={'enabled': False})
    print(f"   Status: {response.status_code}")
    
    # Étape 2: Vérifier le statut
    print("\n📊 ÉTAPE 2: Statut initial")
    response = requests.get(f'{BASE_URL}/users/{username}/protection-status/')
    status = response.json()
    print(f"   Protection: {status['protection_enabled']}")
    print(f"   Tentatives échouées: {status['failed_attempts']}/3")
    print(f"   Verrouillé: {status['is_locked']}")
    
    # Étape 3: Attaque SANS protection
    print("\n" + "─" * 80)
    print("🔓 ÉTAPE 3: Attaque SANS protection")
    print("─" * 80)
    
    start = time.time()
    response = requests.post(f'{BASE_URL}/attack/full_dictionary/', json={
        'target_username': username,
        'max_seconds': 120,
        'dictionary_type': 'digits6'
    })
    elapsed = time.time() - start
    
    result = response.json()
    print(f"   Temps: {elapsed:.2f}s")
    print(f"   Trouvé: {result.get('found', False)}")
    if result.get('found'):
        print(f"   Mot de passe: {result.get('plaintext')}")
        print(f"   Tentatives: {result.get('attempts')}")
    
    # Vérifier si le compte est affecté
    response = requests.get(f'{BASE_URL}/users/{username}/protection-status/')
    status = response.json()
    print(f"\n   Après attaque:")
    print(f"   • Tentatives échouées: {status['failed_attempts']}/3")
    print(f"   • Verrouillé: {status['is_locked']}")
    
    # Étape 4: Activer la protection
    print("\n" + "─" * 80)
    print("🛡️  ÉTAPE 4: Activation de la protection")
    print("─" * 80)
    
    response = requests.post(f'{BASE_URL}/users/{username}/toggle-protection/', 
                            json={'enabled': True})
    print(f"   ✅ Protection activée")
    
    # Étape 5: Attaque AVEC protection
    print("\n" + "─" * 80)
    print("🔐 ÉTAPE 5: Attaque AVEC protection activée")
    print("─" * 80)
    print("   Question: L'attaque va-t-elle être ralentie/bloquée ?")
    
    start = time.time()
    response = requests.post(f'{BASE_URL}/attack/full_dictionary/', json={
        'target_username': username,
        'max_seconds': 120,
        'dictionary_type': 'digits6'
    })
    elapsed = time.time() - start
    
    result = response.json()
    print(f"\n   Temps: {elapsed:.2f}s")
    print(f"   Trouvé: {result.get('found', False)}")
    if result.get('found'):
        print(f"   Mot de passe: {result.get('plaintext')}")
        print(f"   Tentatives: {result.get('attempts')}")
    
    # Vérifier l'impact
    response = requests.get(f'{BASE_URL}/users/{username}/protection-status/')
    status = response.json()
    print(f"\n   Après attaque avec protection:")
    print(f"   • Tentatives échouées: {status['failed_attempts']}/3")
    print(f"   • Verrouillé: {status['is_locked']}")
    
    # Analyse
    print("\n" + "=" * 80)
    print("  📊 ANALYSE")
    print("=" * 80)
    
    print("\n🔍 CONSTAT:")
    print("   Les attaques par dictionnaire/force brute")
    print("   NE PASSENT PAS par l'endpoint /login/")
    print("   Elles déchiffrent DIRECTEMENT le mot de passe")
    print("   Sans appeler login_user() ou record_failed_attempt()")
    
    print("\n⚠️  CONSÉQUENCE:")
    print("   La protection N'AFFECTE PAS les attaques automatiques!")
    print("   Elle protège uniquement contre les tentatives de login manuelles")
    
    print("\n💡 SOLUTION:")
    print("   Pour protéger contre les attaques, il faut:")
    print("   1. Ajouter une vérification dans les endpoints d'attaque")
    print("   2. Limiter le nombre d'attaques par compte/IP")
    print("   3. Ou faire passer les attaques par le système de login")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    main()
