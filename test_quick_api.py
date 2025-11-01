"""
Test rapide de l'API avec dictionnaire par défaut
"""
import requests
import json
import time

# Attendre un peu que le serveur démarre
time.sleep(2)

BASE_URL = "http://127.0.0.1:8000"

def test_dictionary_type(dict_type):
    """Teste un type de dictionnaire"""
    url = f"{BASE_URL}/api/attack/dictionary"
    
    payload = {
        "target_username": "bellia",
        "dictionary_type": dict_type,
        "max_seconds": 60,
        "limit": 0
    }
    
    print(f"\n{'='*60}")
    print(f"Test avec dictionnaire: '{dict_type}'")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'dictionary_info' in data:
                info = data['dictionary_info']
                print(f"✅ Dictionnaire: {info['type']}")
                print(f"   Taille: {info['size']:,} entrées")
                print(f"   Temps: {data.get('time_elapsed_seconds', 0):.4f}s")
                print(f"   Matches: {len(data.get('matches', []))}")
                
                if data.get('matches'):
                    for match in data['matches']:
                        print(f"   → Password trouvé: {match['candidate_key'].get('password_candidate', 'N/A')}")
            else:
                print("⚠️  Pas d'info dictionnaire dans la réponse")
                print(f"Réponse: {json.dumps(data, indent=2)[:500]}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Réponse: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    print("\n🧪 Test API - Dictionnaires")
    
    # Test 1: Dictionnaire par défaut
    test_dictionary_type("default")
    
    # Test 2: Dictionnaire 012
    test_dictionary_type("012")
    
    # Test 3: Dictionnaire test (petits mots de passe communs)
    test_dictionary_type("test")
    
    print(f"\n{'='*60}")
    print("✅ Tests terminés!")
    print(f"{'='*60}\n")
