"""
Test de l'API d'attaque par dictionnaire depuis le frontend
"""
import requests
import json

print("="*80)
print(" TEST API ATTAQUE DICTIONNAIRE")
print("="*80)

url = "http://127.0.0.1:8000/attack/full_dictionary/"

# Test avec l'utilisateur bellia
payload = {
    "target_username": "bellia",
    "max_seconds": 60,
    "limit": 0
}

print(f"\n1. URL: {url}")
print(f"2. Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\n3. Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n4. ✅ SUCCÈS!")
        print(f"\nRésultats:")
        print(f"  - Target: {result.get('target_username')}")
        print(f"  - Algorithm: {result.get('algorithm')}")
        print(f"  - Mode: {result.get('mode')}")
        print(f"  - Attempts: {result.get('attempts')}")
        print(f"  - Time: {result.get('time_sec')} secondes")
        print(f"  - Matches count: {result.get('matches_count')}")
        
        if result.get('matches_count', 0) > 0:
            print(f"\n✅ MOT DE PASSE TROUVÉ!")
            for i, match in enumerate(result['matches'][:5], 1):
                print(f"\n  Match {i}:")
                print(f"    - Plaintext: {match.get('candidate_plaintext')}")
                print(f"    - Password: {match.get('candidate_key', {}).get('password_candidate')}")
                print(f"    - Confidence: {match.get('confidence')}")
        else:
            print(f"\n❌ Aucun match trouvé")
            if result.get('errors'):
                print(f"  Erreurs: {result.get('errors')}")
    else:
        print(f"\n❌ ERREUR {response.status_code}")
        try:
            error = response.json()
            print(f"  Message: {error.get('error', response.text)}")
        except:
            print(f"  Response: {response.text}")
            
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

print("\n" + "="*80)
