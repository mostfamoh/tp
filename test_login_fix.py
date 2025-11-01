#!/usr/bin/env python
"""
Test rapide du login après correction
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def test_login(username, password):
    """Teste une connexion"""
    url = f'{BASE_URL}/login/'
    data = {
        'username': username,
        'password': password
    }
    
    print(f"\n🔑 Test de connexion:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    
    try:
        response = requests.post(url, json=data)
        print(f"   Status: {response.status_code}")
        
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print(f"   ✅ CONNEXION RÉUSSIE!")
            return True
        else:
            print(f"   ❌ CONNEXION ÉCHOUÉE")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    print("=" * 70)
    print("  🧪 TEST DE CONNEXION APRÈS CORRECTION")
    print("=" * 70)
    
    # Test avec utilisateurs connus
    test_cases = [
        ('mostafa', '111'),
        ('ali', '123456'),
        ('bellia', '123456'),
        ('test_protection', 'ABC'),
        ('demo_quick', 'ABC'),
    ]
    
    successes = 0
    for username, password in test_cases:
        if test_login(username, password):
            successes += 1
    
    print("\n" + "=" * 70)
    print(f"  📊 RÉSULTAT: {successes}/{len(test_cases)} connexions réussies")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
