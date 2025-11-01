"""
Test de la stéganographie (texte et image)
"""

import requests
import json
import base64

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def test_text_steganography():
    """Test de la stéganographie dans le texte"""
    
    print_section("TEST : Stéganographie dans le Texte")
    
    cover_text = """
    La cryptographie est l'art de protéger les informations. 
    Elle utilise des algorithmes mathématiques complexes. 
    Les messages sont transformés en texte chiffré. 
    Seul le destinataire peut déchiffrer le message.
    """
    
    secret_message = "HELLO"
    
    # Test des 3 méthodes
    methods = ['whitespace', 'zerowidth', 'case']
    
    for method in methods:
        print_section(f"MÉTHODE : {method.upper()}")
        
        # Cacher le message
        print(f"📝 Texte de couverture : {len(cover_text)} caractères")
        print(f"🔒 Message secret : '{secret_message}'")
        
        response = requests.post(f"{BASE_URL}/stego/text/hide/", json={
            'cover_text': cover_text,
            'secret_message': secret_message,
            'method': method
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Message caché avec succès")
            print(f"   Méthode : {data.get('method')}")
            print(f"   Explication : {data.get('explanation')}")
            
            stego_text = data.get('stego_text')
            print(f"   Longueur du texte stégano : {len(stego_text)} caractères")
            
            # Extraire le message
            print(f"\n🔍 Extraction du message...")
            
            extract_response = requests.post(f"{BASE_URL}/stego/text/extract/", json={
                'stego_text': stego_text,
                'method': method
            })
            
            if extract_response.status_code == 200:
                extract_data = extract_response.json()
                extracted_message = extract_data.get('secret_message')
                
                print(f"   Message extrait : '{extracted_message}'")
                
                if extracted_message == secret_message:
                    print(f"   ✅ SUCCÈS : Message correctement extrait!")
                else:
                    print(f"   ❌ ÉCHEC : Message différent")
                    print(f"      Attendu : '{secret_message}'")
                    print(f"      Obtenu : '{extracted_message}'")
            else:
                print(f"   ❌ Erreur d'extraction : {extract_response.text}")
        else:
            print(f"❌ Erreur de cachage : {response.text}")


def test_image_steganography():
    """Test de la stéganographie dans les images"""
    
    print_section("TEST : Stéganographie dans les Images")
    
    # Créer une image de test
    print("📸 Création d'une image blanche de test...")
    
    response = requests.get(f"{BASE_URL}/stego/sample-image/?width=400&height=300")
    
    if response.status_code != 200:
        print(f"❌ Erreur de création d'image : {response.text}")
        return
    
    data = response.json()
    image_data = data.get('image_data')
    
    print(f"✅ Image créée : {data.get('width')}x{data.get('height')} pixels")
    
    # Analyser la capacité
    print(f"\n📊 Analyse de la capacité...")
    
    analyze_response = requests.post(f"{BASE_URL}/stego/analyze/image/", json={
        'image_data': image_data
    })
    
    if analyze_response.status_code == 200:
        capacity = analyze_response.json()
        print(f"   Dimensions : {capacity.get('width')}x{capacity.get('height')}")
        print(f"   Pixels totaux : {capacity.get('total_pixels'):,}")
        print(f"   Capacité max : {capacity.get('max_characters'):,} caractères")
        print(f"   Capacité recommandée : {capacity.get('recommended_message_length'):,} caractères")
    
    # Cacher un message
    secret_message = "This is a secret message hidden in an image using LSB steganography!"
    
    print(f"\n🔒 Cachage du message...")
    print(f"   Message secret : '{secret_message}'")
    print(f"   Longueur : {len(secret_message)} caractères")
    
    hide_response = requests.post(f"{BASE_URL}/stego/image/hide/", json={
        'image_data': image_data,
        'secret_message': secret_message,
        'method': 'lsb'
    })
    
    if hide_response.status_code == 200:
        hide_data = hide_response.json()
        print(f"\n✅ Message caché avec succès")
        print(f"   Méthode : {hide_data.get('method')}")
        print(f"   Pixels utilisés : {hide_data.get('pixels_used')}")
        print(f"   Utilisation : {hide_data.get('usage_percent')}%")
        print(f"   Explication : {hide_data.get('explanation')}")
        
        stego_image = hide_data.get('stego_image')
        
        # Extraire le message
        print(f"\n🔍 Extraction du message...")
        
        extract_response = requests.post(f"{BASE_URL}/stego/image/extract/", json={
            'image_data': f'data:image/png;base64,{stego_image}',
            'method': 'lsb'
        })
        
        if extract_response.status_code == 200:
            extract_data = extract_response.json()
            extracted_message = extract_data.get('secret_message')
            
            print(f"   Message extrait : '{extracted_message}'")
            
            if extracted_message == secret_message:
                print(f"   ✅ SUCCÈS : Message correctement extrait!")
            else:
                print(f"   ⚠️  Différence détectée")
                print(f"      Longueur attendue : {len(secret_message)}")
                print(f"      Longueur obtenue : {len(extracted_message)}")
        else:
            print(f"   ❌ Erreur d'extraction : {extract_response.text}")
    else:
        print(f"❌ Erreur de cachage : {hide_response.text}")


def test_methods_info():
    """Affiche les informations sur les méthodes disponibles"""
    
    print_section("MÉTHODES DISPONIBLES")
    
    response = requests.get(f"{BASE_URL}/stego/methods/")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n📝 Méthodes de Stéganographie Texte :")
        for method_id, info in data.get('text_methods', {}).items():
            print(f"\n   {info.get('name')} ({method_id})")
            print(f"   └─ {info.get('description')}")
            print(f"      Visibilité : {info.get('visibility')}")
            print(f"      Robustesse : {info.get('robustness')}")
            print(f"      Capacité : {info.get('capacity')}")
        
        print("\n\n🖼️  Méthodes de Stéganographie Image :")
        for method_id, info in data.get('image_methods', {}).items():
            print(f"\n   {info.get('name')} ({method_id})")
            print(f"   └─ {info.get('description')}")
            print(f"      Visibilité : {info.get('visibility')}")
            print(f"      Robustesse : {info.get('robustness')}")
            print(f"      Capacité : {info.get('capacity')}")
            print(f"      Perte qualité : {info.get('quality_loss')}")
    else:
        print(f"❌ Erreur : {response.text}")


def test_cover_text_analysis():
    """Test d'analyse de texte de couverture"""
    
    print_section("ANALYSE DE TEXTE DE COUVERTURE")
    
    cover_text = """
    La stéganographie est l'art de cacher des messages dans d'autres contenus.
    Contrairement à la cryptographie qui rend le message illisible, la stéganographie
    cache l'existence même du message. Cette technique est utilisée depuis l'antiquité.
    Aujourd'hui, elle peut être appliquée aux textes, images, audio et vidéo.
    """
    
    print(f"📝 Texte à analyser :\n{cover_text}")
    
    response = requests.post(f"{BASE_URL}/stego/analyze/text/", json={
        'text': cover_text
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Résultats de l'analyse :")
        print(f"   Longueur totale : {data.get('total_length')} caractères")
        print(f"   Lettres : {data.get('letters')}")
        print(f"   Mots : {data.get('words')}")
        print(f"   Phrases : {data.get('sentences')}")
        print(f"\n   Capacités :")
        print(f"   ├─ Case-based : {data.get('capacity_case')} caractères max")
        print(f"   ├─ WhiteSpace : {data.get('capacity_whitespace')}")
        print(f"   └─ Zero-Width : {data.get('capacity_zerowidth')}")
    else:
        print(f"❌ Erreur : {response.text}")


def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        TEST DE STÉGANOGRAPHIE - Texte et Image          ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    try:
        # Afficher les méthodes disponibles
        test_methods_info()
        
        # Tester l'analyse de texte
        test_cover_text_analysis()
        
        # Tester la stéganographie texte
        test_text_steganography()
        
        # Tester la stéganographie image
        test_image_steganography()
        
        print_section("CONCLUSION")
        print("""
        ✅ Tests de stéganographie terminés !
        
        Résumé :
        - ✅ Stéganographie texte (3 méthodes : whitespace, zerowidth, case)
        - ✅ Stéganographie image (méthode LSB)
        - ✅ Analyse de capacité (texte et image)
        - ✅ Extraction de messages cachés
        
        La stéganographie permet de :
        1. Cacher des messages dans du texte ou des images
        2. Communiquer de manière discrète
        3. Protéger la confidentialité sans éveiller les soupçons
        """)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Le serveur Django n'est pas accessible.")
        print("   Assurez-vous que le serveur tourne sur http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
