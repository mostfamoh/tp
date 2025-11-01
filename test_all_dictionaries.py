"""
Script pour tester tous les types de dictionnaires via l'API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_dictionary_attack(dict_type, target_username):
    """Teste une attaque avec un type de dictionnaire spécifique"""
    url = f"{BASE_URL}/api/attack/dictionary"
    
    payload = {
        "target_username": target_username,
        "dictionary_type": dict_type,
        "max_seconds": 120,  # 2 minutes max
        "limit": 0
    }
    
    print(f"\n{'='*60}")
    print(f"Test: Attaque sur '{target_username}' avec dictionnaire '{dict_type}'")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Afficher les informations du dictionnaire
            if 'dictionary_info' in data:
                info = data['dictionary_info']
                print(f"\nDictionnaire utilisé:")
                print(f"  Type: {info['type']}")
                print(f"  Taille: {info['size']:,} entrées")
                print(f"  Chemin: {info['path']}")
            
            # Afficher les résultats
            print(f"\nRésultats de l'attaque:")
            print(f"  Temps: {data.get('time_elapsed_seconds', 0):.4f} secondes")
            print(f"  Tentatives: {data.get('attempts_count', 0):,}")
            print(f"  Matches: {len(data.get('matches', []))}")
            
            # Afficher les mots de passe trouvés
            if data.get('matches'):
                print(f"\n✅ Mot(s) de passe trouvé(s):")
                for match in data['matches']:
                    print(f"    - Password: {match['candidate_key'].get('password_candidate', 'N/A')}")
                    print(f"      Plaintext: {match['candidate_plaintext']}")
                    print(f"      Confidence: {match['confidence']}")
            else:
                print("\n❌ Aucun mot de passe trouvé")
                
        else:
            print(f"❌ Erreur: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur Django")
        print("   Assurez-vous que le serveur est démarré: python manage.py runserver")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Test des Dictionnaires d'Attaque - Projet SSAD TP1     ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Test 1: Dictionnaire par défaut (backend/dic.txt - 27 entrées)
    test_dictionary_attack("default", "bellia")
    
    # Test 2: Dictionnaire {0,1,2}³ (27 entrées)
    test_dictionary_attack("012", "cas1_012")
    
    # Test 3: Dictionnaire test (50 mots de passe communs)
    test_dictionary_attack("test", "bellia")
    
    # Test 4: Dictionnaire {0-9}³ (1,000 entrées)
    test_dictionary_attack("digits3", "bellia")
    
    # Test 5: GRAND dictionnaire {0-9}⁶ (1,000,000 entrées)
    print("\n⚠️  ATTENTION: Le test suivant peut prendre plusieurs minutes!")
    print("    Attaque avec 1,000,000 de combinaisons...")
    
    response = input("\nVoulez-vous tester le dictionnaire complet? (o/N): ").strip().lower()
    
    if response == 'o' or response == 'oui':
        test_dictionary_attack("digits6", "cas2_123456")
    else:
        print("\n⏭️  Test du grand dictionnaire ignoré.")
    
    print(f"\n{'='*60}")
    print("Tests terminés!")
    print(f"{'='*60}\n")
    
    print("""
Résumé des dictionnaires disponibles:
  - 'default' : backend/dic.txt (27 entrées)
  - '012'     : backend/dictionaries/dict_012.txt (27 entrées)
  - 'test'    : backend/dictionaries/dict_test.txt (50 entrées)
  - 'digits3' : backend/dictionaries/dict_digits3.txt (1,000 entrées)
  - 'digits6' : backend/dictionaries/dict_digits6.txt (1,000,000 entrées)

Pour utiliser dans le frontend, envoyez:
  {
    "target_username": "bellia",
    "dictionary_type": "012",
    "max_seconds": 60,
    "limit": 0
  }
""")
