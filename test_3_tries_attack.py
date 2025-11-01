"""
Test pour vérifier le système de 3 TENTATIVES lors des attaques
La protection ne bloque plus immédiatement, mais compte les tentatives
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def get_protection_status(username):
    """Récupère le statut de protection d'un compte"""
    response = requests.get(f"{BASE_URL}/users/{username}/protection-status/")
    if response.status_code == 200:
        return response.json()
    return None

def display_status(username):
    """Affiche le statut actuel du compte"""
    status = get_protection_status(username)
    if status:
        locked = "🔒 OUI" if status.get('is_locked') else "🔓 Non"
        print(f"   Compte : {username}")
        print(f"   Protection : {'🟢 Activée' if status.get('protection_enabled') else '🔴 Désactivée'}")
        print(f"   Tentatives échouées : {status.get('failed_attempts')}/3")
        print(f"   Compte verrouillé : {locked}")
        if status.get('is_locked'):
            print(f"   Temps restant : {status.get('remaining_minutes')} min")

def test_3_tries_system():
    """Test complet du système de 3 tentatives"""
    
    username = "bellia"
    
    print_section("TEST : Système de 3 tentatives avec attaques")
    print(f"🎯 Compte testé : {username}")
    print(f"📝 Le mot de passe correct est : BCDEFG (converti de 123456)")
    
    # ÉTAPE 0: Réinitialiser le compte
    print_section("ÉTAPE 0: Préparation du compte")
    
    # Désactiver protection
    requests.post(f"{BASE_URL}/users/{username}/toggle-protection/", json={'enabled': False})
    # Débloquer si besoin
    requests.post(f"{BASE_URL}/users/{username}/unlock/")
    # Activer protection
    response = requests.post(f"{BASE_URL}/users/{username}/toggle-protection/", json={'enabled': True})
    
    if response.status_code == 200:
        print(f"✅ Compte préparé avec protection activée")
        display_status(username)
    else:
        print(f"❌ Erreur de préparation: {response.text}")
        return
    
    # ÉTAPE 1: Première attaque (doit échouer mais autoriser l'exécution)
    print_section("ÉTAPE 1: Première tentative d'attaque (mauvais dictionnaire)")
    print("   Dictionnaire : 'test' (ne contient pas le bon mot de passe)")
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'test',
        'max_seconds': 3
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Attaque exécutée")
        print(f"   Tentatives testées : {data.get('attempts', 0)}")
        print(f"   Résultats trouvés : {data.get('matches_count', 0)}")
        print(f"   Temps : {data.get('time_sec', 0):.2f}s")
        
        if 'protection_active' in data:
            print(f"\n   🛡️ Protection détectée :")
            print(f"      Tentatives échouées : {data.get('failed_attempts', 0)}/3")
            print(f"      Tentatives restantes : {data.get('attempts_left', 0)}")
            if 'warning' in data:
                print(f"      ⚠️ {data['warning']}")
    elif response.status_code == 403:
        print(f"🔒 Attaque bloquée (compte déjà verrouillé)")
        print(f"   {response.json().get('message')}")
    
    print("\n   📊 Statut après tentative 1 :")
    display_status(username)
    
    # ÉTAPE 2: Deuxième attaque
    print_section("ÉTAPE 2: Deuxième tentative d'attaque")
    
    time.sleep(1)  # Petit délai entre attaques
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'test',
        'max_seconds': 3
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Attaque exécutée")
        print(f"   Résultats trouvés : {data.get('matches_count', 0)}")
        
        if 'protection_active' in data:
            print(f"\n   🛡️ Protection :")
            print(f"      Tentatives échouées : {data.get('failed_attempts', 0)}/3")
            print(f"      Tentatives restantes : {data.get('attempts_left', 0)}")
            if 'warning' in data:
                print(f"      ⚠️ {data['warning']}")
    elif response.status_code == 403:
        print(f"🔒 Compte verrouillé")
    
    print("\n   📊 Statut après tentative 2 :")
    display_status(username)
    
    # ÉTAPE 3: Troisième attaque (dernière chance!)
    print_section("ÉTAPE 3: Troisième tentative d'attaque (DERNIÈRE CHANCE)")
    
    time.sleep(1)
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'test',
        'max_seconds': 3
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Attaque exécutée")
        print(f"   Résultats trouvés : {data.get('matches_count', 0)}")
        
        if 'protection_active' in data:
            print(f"\n   🛡️ Protection :")
            print(f"      Tentatives échouées : {data.get('failed_attempts', 0)}/3")
            print(f"      Tentatives restantes : {data.get('attempts_left', 0)}")
            
            if data.get('account_locked'):
                print(f"\n   🔒 COMPTE VERROUILLÉ !")
                print(f"      {data.get('locked_message')}")
    elif response.status_code == 403:
        print(f"🔒 Compte déjà verrouillé")
    
    print("\n   📊 Statut après tentative 3 :")
    display_status(username)
    
    # ÉTAPE 4: Quatrième tentative (doit être bloquée)
    print_section("ÉTAPE 4: Quatrième tentative (devrait être BLOQUÉE)")
    
    time.sleep(1)
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'test',
        'max_seconds': 3
    })
    
    if response.status_code == 403:
        data = response.json()
        print(f"🔒 ATTAQUE BLOQUÉE (comme attendu)")
        print(f"   Code HTTP : {response.status_code}")
        print(f"   Erreur : {data.get('error')}")
        print(f"   Message : {data.get('message')}")
        if 'remaining_minutes' in data:
            print(f"   Temps restant : {data.get('remaining_minutes')} minutes")
    elif response.status_code == 200:
        print(f"⚠️ PROBLÈME : L'attaque a été exécutée alors que le compte devrait être verrouillé!")
    
    print("\n   📊 Statut final :")
    display_status(username)
    
    # ÉTAPE 5: Test du déverrouillage manuel
    print_section("ÉTAPE 5: Déverrouillage manuel")
    
    response = requests.post(f"{BASE_URL}/users/{username}/unlock/")
    if response.status_code == 200:
        print(f"✅ Compte déverrouillé avec succès")
        print("\n   📊 Statut après déverrouillage :")
        display_status(username)
    
    # ÉTAPE 6: Attaque réussie après déverrouillage
    print_section("ÉTAPE 6: Attaque avec le BON dictionnaire (après déverrouillage)")
    print("   Utilisation d'un dictionnaire contenant 'BCDEFG'")
    
    # D'abord créer un dictionnaire temporaire avec le bon mot
    import os
    temp_dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_correct.txt')
    os.makedirs(os.path.dirname(temp_dict_path), exist_ok=True)
    with open(temp_dict_path, 'w') as f:
        f.write('BCDEFG\n')  # Le mot de passe correct
        f.write('WRONG1\n')
        f.write('WRONG2\n')
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'test',  # On va le charger depuis le dict test
        'max_seconds': 3
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Attaque exécutée")
        print(f"   Résultats trouvés : {data.get('matches_count', 0)}")
        
        if data.get('matches_count', 0) > 0:
            print(f"   🎉 MOT DE PASSE TROUVÉ !")
            print(f"   ✅ Le compteur devrait être réinitialisé (attaque réussie)")
        else:
            print(f"   ❌ Mot de passe non trouvé")
            if 'protection_active' in data:
                print(f"   ⚠️ Tentatives restantes : {data.get('attempts_left', 0)}")
    
    print("\n   📊 Statut final :")
    display_status(username)
    
    # CONCLUSION
    print_section("CONCLUSION")
    print("""
    ✅ SYSTÈME DE 3 TENTATIVES :
    
    Comportement attendu :
    1️⃣ Tentative 1 : Attaque exécutée, compteur → 1/3
    2️⃣ Tentative 2 : Attaque exécutée, compteur → 2/3
    3️⃣ Tentative 3 : Attaque exécutée, compteur → 3/3 → VERROUILLAGE
    4️⃣ Tentative 4 : BLOQUÉE (403 Forbidden)
    
    Caractéristiques :
    - ✅ Les attaques ÉCHOUÉES incrémentent le compteur
    - ✅ Les attaques RÉUSSIES réinitialisent le compteur
    - ✅ Après 3 échecs, compte verrouillé pour 30 minutes
    - ✅ Déverrouillage manuel possible
    - ✅ Messages d'avertissement à chaque tentative
    
    Différence avec l'ancien système :
    - ❌ AVANT : Blocage immédiat si protection activée
    - ✅ MAINTENANT : Système de 3 chances avant verrouillage
    """)

if __name__ == '__main__':
    try:
        test_3_tries_system()
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Le serveur Django n'est pas accessible.")
        print("   Assurez-vous que le serveur tourne sur http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
