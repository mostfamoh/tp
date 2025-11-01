"""
Script pour voir le traceback complet de l'erreur
"""
import requests

url = "http://127.0.0.1:8000/api/attack/dictionary"
payload = {
    "target_username": "bellia",
    "dictionary_type": "default",
    "max_seconds": 60,
    "limit": 0
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}\n")
    
    # Afficher tout le contenu HTML pour voir le traceback
    if response.status_code == 500:
        # Sauvegarder dans un fichier HTML
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Page d'erreur sauvegardée dans: error_page.html")
        print("   Ouvrez ce fichier dans un navigateur pour voir le traceback complet.")
    else:
        print(response.text)
        
except Exception as e:
    print(f"Erreur: {e}")
