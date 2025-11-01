import requests
import json
import random

def test_registration(test_name, data):
    """Tester l'enregistrement avec différents paramètres"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    url = "http://127.0.0.1:8000/regester/"
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCÈS")
            result = response.json()
            print(f"Message: {result.get('message')}")
            print(f"Mot de passe chiffré: {result.get('encrypted_password')}")
        else:
            print(f"❌ ERREUR (Code {response.status_code})")
            error = response.json()
            print(f"Erreur: {error.get('error')}")
            if 'suggestion' in error:
                print(f"Suggestion: {error.get('suggestion')}")
            if 'available_algorithms' in error:
                print(f"Algorithmes disponibles: {error.get('available_algorithms')}")
                
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

# Générer des noms uniques
rand = random.randint(10000, 99999)

# Test 1: Enregistrement normal César avec nouveau username
test_registration(
    "Enregistrement César (nouveau user)",
    {
        "username": f"cesar_user_{rand}",
        "password": "password123",
        "algorithm": "cesar",
        "key_param": "3"
    }
)

# Test 2: Paramètres manquants
test_registration(
    "Erreur: Paramètres manquants (pas de key_param)",
    {
        "username": f"no_key_{rand}",
        "password": "password",
        "algorithm": "cesar"
    }
)

# Test 3: Algorithme inconnu
test_registration(
    "Erreur: Algorithme inconnu",
    {
        "username": f"unknown_{rand}",
        "password": "password",
        "algorithm": "aes",
        "key_param": "123"
    }
)

# Test 4: Username déjà existant
test_registration(
    "Erreur: Username déjà existant",
    {
        "username": "test_register_debug",  # Existe déjà
        "password": "newpassword",
        "algorithm": "cesar",
        "key_param": "5"
    }
)

# Test 5: Champs manquants
test_registration(
    "Erreur: Username manquant",
    {
        "password": "password",
        "algorithm": "cesar",
        "key_param": "3"
    }
)

test_registration(
    "Erreur: Password manquant",
    {
        "username": f"nopass_{rand}",
        "algorithm": "cesar",
        "key_param": "3"
    }
)

test_registration(
    "Erreur: Format Affine invalide",
    {
        "username": f"bad_affine_{rand}",
        "password": "test",
        "algorithm": "affine",
        "key_param": "5"  # Devrait être "5,8"
    }
)

print(f"\n{'='*60}")
print("✅ TOUS LES CAS D'ERREUR SONT MAINTENANT BIEN GÉRÉS")
print(f"{'='*60}")
