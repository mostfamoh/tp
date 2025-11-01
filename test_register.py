import requests
import json

# Test d'enregistrement
url = "http://127.0.0.1:8000/regester/"

test_data = {
    "username": "test_register_debug",
    "password": "testpass123",
    "algorithm": "cesar",
    "key_param": "5"
}

try:
    response = requests.post(url, json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"\nJSON Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Erreur: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
