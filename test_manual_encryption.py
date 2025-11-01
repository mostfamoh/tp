"""
Test manuel du processus de chiffrement et comparaison
"""

from backend.cryptotoolbox.attack.utils import clean_text

# Simuler ce qui se passe
password_original = "012"
password_converted = clean_text(password_original)  # "012" -> "ABC"

print("="*80)
print(" TEST MANUEL DU CHIFFREMENT")
print("="*80)

print(f"\n1. Mot de passe original: {password_original}")
print(f"2. Après clean_text: {password_converted}")

# Chiffrer avec shift=3
shift = 3
encrypted = ''.join(chr((ord(ch) - 65 + shift) % 26 + 65) for ch in password_converted)
print(f"3. Chiffré (shift={shift}): {encrypted}")

# Maintenant vérifier l'utilisateur dans la DB
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser

user = CustomUser.objects.filter(username='cas1_012').first()
if user:
    print(f"\n4. Utilisateur trouvé dans la DB:")
    print(f"   - Username: {user.username}")
    print(f"   - Password encrypted: {user.password_encypted}")
    print(f"   - Algorithm: {user.algorithm}")
    print(f"   - Key data: {user.key_data}")
    
    print(f"\n5. Comparaison:")
    print(f"   Notre chiffrement: {encrypted}")
    print(f"   DB chiffrement:    {user.password_encypted}")
    print(f"   Match: {encrypted == user.password_encypted}")
    
    # Tester l'attaque dictionnaire manuellement
    print(f"\n6. Test attaque dictionnaire:")
    dictionary = ['000', '001', '002', '010', '011', '012']
    
    for word in dictionary:
        word_cleaned = clean_text(word)
        word_encrypted = ''.join(chr((ord(ch) - 65 + shift) % 26 + 65) for ch in word_cleaned)
        match = word_encrypted == user.password_encypted
        status = "✅ TROUVE" if match else "❌"
        print(f"   {word} -> {word_cleaned} -> {word_encrypted} {status}")
        if match:
            print(f"   >>> MOT DE PASSE TROUVE: {word}")
            break
else:
    print("\n❌ Utilisateur 'cas1_012' non trouvé dans la base de données")
    print("   Exécutez d'abord: python demonstration_partie3.py")
