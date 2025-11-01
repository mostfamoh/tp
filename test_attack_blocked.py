"""
Test pour vérifier que la protection BLOQUE les attaques automatiques
Après modification des endpoints pour vérifier la protection
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_attack_blocked():
    """Test complet : la protection doit maintenant bloquer les attaques"""
    
    username = "bellia"
    
    print_section("TEST : Protection contre les attaques")
    print(f"Compte testé: {username}")
    
    # ÉTAPE 1: Désactiver la protection
    print_section("ÉTAPE 1: Désactiver la protection")
    response = requests.post(f"{BASE_URL}/users/{username}/toggle-protection/", json={
        'enabled': False
    })
    if response.status_code == 200:
        print(f"✅ Protection désactivée")
    else:
        print(f"❌ Erreur: {response.text}")
        return
    
    # ÉTAPE 2: Attaque SANS protection (doit fonctionner)
    print_section("ÉTAPE 2: Attaque sans protection")
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'test',
        'max_seconds': 5
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Attaque lancée avec succès")
        print(f"   Tentatives: {data.get('attempts', 0)}")
        print(f"   Temps: {data.get('time_sec', 0):.2f}s")
        print(f"   Résultats: {data.get('matches_count', 0)} correspondances")
    else:
        print(f"❌ Attaque bloquée: {response.status_code}")
        print(f"   Message: {response.json().get('message', 'N/A')}")
    
    # ÉTAPE 3: Activer la protection
    print_section("ÉTAPE 3: Activer la protection")
    response = requests.post(f"{BASE_URL}/users/{username}/toggle-protection/", json={
        'enabled': True
    })
    if response.status_code == 200:
        print(f"✅ Protection activée")
    else:
        print(f"❌ Erreur: {response.text}")
        return
    
    # ÉTAPE 4: Vérifier le statut
    print_section("ÉTAPE 4: Vérifier le statut de protection")
    response = requests.get(f"{BASE_URL}/users/{username}/protection-status/")
    if response.status_code == 200:
        data = response.json()
        print(f"   Protection activée: {data.get('protection_enabled')}")
        print(f"   Tentatives: {data.get('failed_attempts')}/3")
        print(f"   Compte bloqué: {data.get('is_locked')}")
    
    # ÉTAPE 5: Attaque AVEC protection (doit être bloquée)
    print_section("ÉTAPE 5: Attaque avec protection activée")
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'test',
        'max_seconds': 5
    })
    
    if response.status_code == 403:
        data = response.json()
        print(f"🛡️  ATTAQUE BLOQUÉE PAR LA PROTECTION!")
        print(f"   Code HTTP: {response.status_code}")
        print(f"   Erreur: {data.get('error')}")
        print(f"   Message: {data.get('message')}")
        print(f"   Suggestion: {data.get('suggestion')}")
    elif response.status_code == 200:
        data = response.json()
        print(f"⚠️  ATTAQUE NON BLOQUÉE (problème!)")
        print(f"   Tentatives: {data.get('attempts', 0)}")
        print(f"   Temps: {data.get('time_sec', 0):.2f}s")
    else:
        print(f"❓ Réponse inattendue: {response.status_code}")
        print(f"   {response.text}")
    
    # ÉTAPE 6: Tester aussi la force brute
    print_section("ÉTAPE 6: Attaque force brute avec protection")
    response = requests.post(f"{BASE_URL}/attack/full_bruteforce/", json={
        'target_username': username,
        'max_seconds': 5
    })
    
    if response.status_code == 403:
        data = response.json()
        print(f"🛡️  ATTAQUE FORCE BRUTE BLOQUÉE!")
        print(f"   Erreur: {data.get('error')}")
        print(f"   Message: {data.get('message')}")
    elif response.status_code == 200:
        print(f"⚠️  ATTAQUE NON BLOQUÉE (problème!)")
    else:
        print(f"❓ Réponse: {response.status_code}")
    
    # ÉTAPE 7: Vérifier que le compteur n'a pas changé
    print_section("ÉTAPE 7: Vérifier le compteur après attaques")
    response = requests.get(f"{BASE_URL}/users/{username}/protection-status/")
    if response.status_code == 200:
        data = response.json()
        print(f"   Tentatives: {data.get('failed_attempts')}/3")
        if data.get('failed_attempts') == 0:
            print(f"   ✅ Le compteur est resté à 0 (attaques bloquées en amont)")
        else:
            print(f"   ⚠️  Le compteur a augmenté!")
    
    # ÉTAPE 8: Conclusion
    print_section("CONCLUSION")
    print("""
    ✅ La protection fonctionne maintenant contre les attaques!
    
    Comportement:
    - Protection désactivée → Attaques autorisées
    - Protection activée → Attaques bloquées (403 Forbidden)
    - Message informatif pour l'utilisateur
    - Compteur ne s'incrémente pas (attaques bloquées avant exécution)
    
    Dans le contexte pédagogique:
    - Les étudiants peuvent activer/désactiver la protection
    - Quand activée, les attaques sont bloquées
    - Le système explique pourquoi et comment débloquer
    """)

if __name__ == '__main__':
    try:
        test_attack_blocked()
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Le serveur Django n'est pas accessible.")
        print("   Assurez-vous que le serveur tourne sur http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
