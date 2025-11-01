"""
Générer les dictionnaires complets pour les attaques
"""
import itertools
import os

print("="*80)
print(" GÉNÉRATION DES DICTIONNAIRES")
print("="*80)

# Créer le dossier backend/dictionaries
dict_dir = 'backend/dictionaries'
os.makedirs(dict_dir, exist_ok=True)

# ============================================================================
# 1. Dictionnaire pour {0,1,2} - 3 caractères (27 combinaisons)
# ============================================================================
print("\n1. Génération dictionnaire {0,1,2} - 3 caractères...")
charset_012 = '012'
length_3 = 3
combinations_012 = [''.join(p) for p in itertools.product(charset_012, repeat=length_3)]

dict_012_path = os.path.join(dict_dir, 'dict_012.txt')
with open(dict_012_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(combinations_012))

print(f"   ✅ {len(combinations_012)} combinaisons générées")
print(f"   📁 Fichier: {dict_012_path}")
print(f"   Exemples: {combinations_012[:5]} ... {combinations_012[-3:]}")

# ============================================================================
# 2. Dictionnaire pour {0-9} - 6 caractères (1,000,000 combinaisons)
# ============================================================================
print("\n2. Génération dictionnaire {0-9} - 6 caractères...")
print("   ⚠️  ATTENTION: 1 million de combinaisons, cela peut prendre du temps...")

charset_digits = '0123456789'
length_6 = 6

dict_digits_path = os.path.join(dict_dir, 'dict_digits6.txt')

# Générer par blocs pour économiser la mémoire
block_size = 100000
total = 0

with open(dict_digits_path, 'w', encoding='utf-8') as f:
    block = []
    for combo in itertools.product(charset_digits, repeat=length_6):
        block.append(''.join(combo))
        total += 1
        
        if len(block) >= block_size:
            f.write('\n'.join(block) + '\n')
            block = []
            
            if total % 100000 == 0:
                print(f"   Progression: {total:,} / 1,000,000")
    
    # Écrire le dernier bloc
    if block:
        f.write('\n'.join(block))

print(f"   ✅ {total:,} combinaisons générées")
print(f"   📁 Fichier: {dict_digits_path}")
print(f"   💾 Taille: ~{os.path.getsize(dict_digits_path) / (1024*1024):.2f} MB")

# ============================================================================
# 3. Dictionnaire pour {0-9} - 3 caractères (1,000 combinaisons)
# ============================================================================
print("\n3. Génération dictionnaire {0-9} - 3 caractères...")
combinations_digits3 = [''.join(p) for p in itertools.product(charset_digits, repeat=3)]

dict_digits3_path = os.path.join(dict_dir, 'dict_digits3.txt')
with open(dict_digits3_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(combinations_digits3))

print(f"   ✅ {len(combinations_digits3)} combinaisons générées")
print(f"   📁 Fichier: {dict_digits3_path}")

# ============================================================================
# 4. Mettre à jour backend/dic.txt avec {0,1,2}
# ============================================================================
print("\n4. Mise à jour de backend/dic.txt...")
main_dict_path = 'backend/dic.txt'
with open(main_dict_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(combinations_012))

print(f"   ✅ backend/dic.txt mis à jour avec {len(combinations_012)} combinaisons")

# ============================================================================
# 5. Créer un dictionnaire combiné pour tests rapides
# ============================================================================
print("\n5. Création d'un dictionnaire de test rapide...")
# Combinaisons courantes + quelques exemples
test_dict = [
    # {0,1,2}^3
    *combinations_012,
    # Mots de passe numériques courants
    '123', '456', '789', '000', '111', '222', '333', '444', '555',
    '666', '777', '888', '999',
    '123456', '654321', '000000', '111111', '222222', '123123',
    '456456', '789789', '012345', '543210'
]

dict_test_path = os.path.join(dict_dir, 'dict_test.txt')
with open(dict_test_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(test_dict))

print(f"   ✅ {len(test_dict)} combinaisons dans dict_test.txt")

print("\n" + "="*80)
print(" ✅ TERMINÉ")
print("="*80)

print("\nRésumé des fichiers créés:")
print(f"  1. {dict_012_path} - 27 combinaisons {'{0,1,2}^3'}")
print(f"  2. {dict_digits3_path} - 1,000 combinaisons {'{0-9}^3'}")
print(f"  3. {dict_digits_path} - 1,000,000 combinaisons {'{0-9}^6'}")
print(f"  4. {dict_test_path} - {len(test_dict)} combinaisons courantes")
print(f"  5. {main_dict_path} - Mis à jour avec {'{0,1,2}^3'}")

print("\n⚠️  IMPORTANT pour les attaques:")
print("  - {0,1,2}^3: Utiliser dict_012.txt (rapide, 27 combinaisons)")
print("  - {0-9}^6: Utiliser dict_digits6.txt (lent, 1M combinaisons)")
print("  - Tests rapides: Utiliser dict_test.txt")
