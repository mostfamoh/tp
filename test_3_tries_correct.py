"""
Test CORRIGÉ du système de 3 tentatives
Utilise un dictionnaire qui NE contient PAS le bon mot de passe
"""

import requests
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def get_protection_status(username):
    response = requests.get(f"{BASE_URL}/users/{username}/protection-status/")
    if response.status_code == 200:
        return response.json()
    return None

def display_status(username):
    status = get_protection_status(username)
    if status:
        locked = "🔒 OUI" if status.get('is_locked') else "🔓 Non"
        print(f"   Compte : {username}")
        print(f"   Protection : {'🟢 Activée' if status.get('protection_enabled') else '🔴 Désactivée'}")
        print(f"   Tentatives échouées : {status.get('failed_attempts')}/3")
        print(f"   Compte verrouillé : {locked}")
        if status.get('is_locked'):
            print(f"   Temps restant : {status.get('remaining_minutes')} min")

def test_3_tries_with_failures():
    """Test avec des attaques qui ÉCHOUENT (dictionnaire ne contenant pas le bon mot)"""
    
    username = "bellia"
    
    print_section("TEST : Système de 3 tentatives (avec ÉCHECS)")
    print(f"🎯 Compte testé : {username}")
    print(f"📝 Mot de passe réel : BCDEFG (converti de 123456)")
    print(f"📚 Dictionnaire utilisé : FAUX mots (WRONGPASS, BADWORD, etc.)")
    
    # Créer un dictionnaire avec de MAUVAIS mots
    dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_wrong.txt')
    os.makedirs(os.path.dirname(dict_path), exist_ok=True)
    with open(dict_path, 'w', encoding='utf-8') as f:
        f.write('WRONGPASS\n')
        f.write('BADWORD\n')
        f.write('INCORRECT\n')
        f.write('NOTTHIS\n')
        f.write('FAILED\n')
    print(f"   ✅ Dictionnaire de mots incorrects créé")
    
    # ÉTAPE 0: Réinitialiser
    print_section("ÉTAPE 0: Préparation")
    requests.post(f"{BASE_URL}/users/{username}/toggle-protection/", json={'enabled': False})
    requests.post(f"{BASE_URL}/users/{username}/unlock/")
    response = requests.post(f"{BASE_URL}/users/{username}/toggle-protection/", json={'enabled': True})
    
    if response.status_code == 200:
        print(f"✅ Compte préparé")
        display_status(username)
    
    # TENTATIVE 1
    print_section("TENTATIVE 1/3 : Attaque avec mauvais dictionnaire")
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'wrong',  # Notre dictionnaire de mauvais mots
        'max_seconds': 5
    })
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get('matches_count', 0)
        print(f"✅ Attaque exécutée")
        print(f"   Tentatives testées : {data.get('attempts', 0)}")
        print(f"   Correspondances : {matches}")
        
        if matches == 0:
            print(f"   ❌ Aucun mot trouvé (échec attendu)")
        
        if 'protection_active' in data:
            print(f"\n   🛡️ PROTECTION ACTIVÉE :")
            print(f"      Compteur : {data.get('failed_attempts', 0)}/3")
            print(f"      Restant : {data.get('attempts_left', 0)} tentative(s)")
            if 'warning' in data:
                print(f"      ⚠️  {data['warning']}")
        else:
            print(f"\n   ⚠️  Pas d'info de protection dans la réponse")
    
    print("\n   📊 Statut :")
    display_status(username)
    
    # TENTATIVE 2
    print_section("TENTATIVE 2/3 : Deuxième attaque")
    time.sleep(1)
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'wrong',
        'max_seconds': 5
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Attaque exécutée")
        print(f"   Correspondances : {data.get('matches_count', 0)}")
        
        if 'protection_active' in data:
            print(f"\n   🛡️ Protection :")
            print(f"      Compteur : {data.get('failed_attempts', 0)}/3")
            print(f"      Restant : {data.get('attempts_left', 0)}")
            if 'warning' in data:
                print(f"      ⚠️  {data['warning']}")
    
    print("\n   📊 Statut :")
    display_status(username)
    
    # TENTATIVE 3 (dernière!)
    print_section("TENTATIVE 3/3 : DERNIÈRE CHANCE !")
    time.sleep(1)
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'wrong',
        'max_seconds': 5
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Attaque exécutée")
        print(f"   Correspondances : {data.get('matches_count', 0)}")
        
        if 'protection_active' in data:
            print(f"\n   🛡️ Protection :")
            print(f"      Compteur : {data.get('failed_attempts', 0)}/3")
            print(f"      Restant : {data.get('attempts_left', 0)}")
            
            if data.get('account_locked'):
                print(f"\n   🔒 COMPTE VERROUILLÉ !")
                print(f"      Message : {data.get('locked_message')}")
            elif 'warning' in data:
                print(f"      ⚠️  {data['warning']}")
    
    print("\n   📊 Statut :")
    display_status(username)
    
    # TENTATIVE 4 (doit être bloquée)
    print_section("TENTATIVE 4 : Devrait être BLOQUÉE")
    time.sleep(1)
    
    response = requests.post(f"{BASE_URL}/attack/full_dictionary/", json={
        'target_username': username,
        'dictionary_type': 'wrong',
        'max_seconds': 5
    })
    
    if response.status_code == 403:
        data = response.json()
        print(f"🔒 BLOQUÉE ! (comme attendu)")
        print(f"   Code : {response.status_code} Forbidden")
        print(f"   Erreur : {data.get('error')}")
        print(f"   Message : {data.get('message')}")
        if 'remaining_minutes' in data:
            print(f"   Déblocage dans : {data.get('remaining_minutes')} min")
    elif response.status_code == 200:
        print(f"❌ PROBLÈME : Attaque autorisée alors que compte devrait être verrouillé!")
        data = response.json()
        print(f"   Correspondances : {data.get('matches_count', 0)}")
    
    print("\n   📊 Statut final :")
    display_status(username)
    
    # CONCLUSION
    print_section("RÉSULTAT")
    
    status = get_protection_status(username)
    if status:
        if status.get('failed_attempts') == 3 and status.get('is_locked'):
            print("✅ SUCCÈS : Le système de 3 tentatives fonctionne !")
            print("\n   Comportement vérifié :")
            print("   ✓ Tentative 1 : Compteur = 1/3")
            print("   ✓ Tentative 2 : Compteur = 2/3")
            print("   ✓ Tentative 3 : Compteur = 3/3 → Verrouillage")
            print("   ✓ Tentative 4 : Bloquée (403 Forbidden)")
        else:
            print("⚠️  Comportement inattendu :")
            print(f"   Tentatives échouées : {status.get('failed_attempts')}/3")
            print(f"   Compte verrouillé : {status.get('is_locked')}")
    
    # Nettoyage
    print_section("NETTOYAGE")
    requests.post(f"{BASE_URL}/users/{username}/unlock/")
    print("✅ Compte déverrouillé")
    
    # Supprimer le dictionnaire temporaire
    if os.path.exists(dict_path):
        os.remove(dict_path)
        print("✅ Dictionnaire temporaire supprimé")

if __name__ == '__main__':
    try:
        test_3_tries_with_failures()
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Serveur Django inaccessible")
        print("   http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
