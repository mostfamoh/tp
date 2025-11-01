import requests
import json

def test_registration(test_name, data):
    """Tester l'enregistrement avec différents paramètres"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Données envoyées: {json.dumps(data, indent=2)}")
    
    url = "http://127.0.0.1:8000/regester/"
    
    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCÈS")
            result = response.json()
            print(f"Message: {result.get('message')}")
            print(f"Mot de passe chiffré: {result.get('encrypted_password')}")
        else:
            print("❌ ERREUR")
            try:
                error = response.json()
                print(f"Erreur JSON: {json.dumps(error, indent=2)}")
            except:
                print(f"Réponse texte: {response.text[:500]}")
                
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

# Test 1: Enregistrement normal César
test_registration(
    "Enregistrement César normal",
    {
        "username": "user_cesar_test",
        "password": "monpassword",
        "algorithm": "cesar",
        "key_param": "3"
    }
)

# Test 2: Enregistrement Affine
test_registration(
    "Enregistrement Affine",
    {
        "username": "user_affine_test",
        "password": "password123",
        "algorithm": "affine",
        "key_param": "5,8"
    }
)

# Test 3: Enregistrement Playfair
test_registration(
    "Enregistrement Playfair",
    {
        "username": "user_playfair_test",
        "password": "secret",
        "algorithm": "playfair",
        "key_param": "KEYWORD"
    }
)

# Test 4: Enregistrement Hill
test_registration(
    "Enregistrement Hill (matrice)",
    {
        "username": "user_hill_test",
        "password": "test",
        "algorithm": "hill",
        "key_param": "[[3,3],[2,5]]"
    }
)

# Test 5: Paramètres manquants
test_registration(
    "Paramètres manquants (pas de key_param)",
    {
        "username": "user_no_key",
        "password": "password",
        "algorithm": "cesar"
    }
)

# Test 6: Algorithme inconnu
test_registration(
    "Algorithme inconnu",
    {
        "username": "user_unknown_algo",
        "password": "password",
        "algorithm": "rsa",
        "key_param": "123"
    }
)

# Test 7: Username déjà existant
test_registration(
    "Username déjà existant",
    {
        "username": "test_register_debug",  # Créé précédemment
        "password": "newpassword",
        "algorithm": "cesar",
        "key_param": "5"
    }
)

# Test 8: Caractères spéciaux dans le mot de passe
test_registration(
    "Caractères spéciaux",
    {
        "username": "user_special_chars",
        "password": "P@ssw0rd!#$",
        "algorithm": "cesar",
        "key_param": "7"
    }
)

print(f"\n{'='*60}")
print("TESTS TERMINÉS")
print(f"{'='*60}")
