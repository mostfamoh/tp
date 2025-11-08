from django.shortcuts import render
from .models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt 
import json ,time
from backend.cryptotoolbox import encrypt_with_algorithm ,decrypt_with_algorithm
from backend.cryptotoolbox.cyphers.caesar import caesar_encrypt ,caesar_decrypt
from backend.cryptotoolbox.cyphers.plaiyfair import encrypt_playfair,decrypt_playfair
from backend.cryptotoolbox.cyphers.hill import hill_encrypt,hill_decrypt
from backend.cryptotoolbox.cyphers.affine import decrypt_affine,encrypt_affine
from backend.cryptotoolbox.attack.attack_runner import run_attack
from backend.cryptotoolbox.steganography import (
    hide_text_in_text, extract_text_from_text,
    hide_text_in_image, extract_text_from_image
)
from backend.cryptotoolbox.steganography.text_stego import get_available_methods, analyze_cover_text
from backend.cryptotoolbox.steganography.image_stego import analyze_image_capacity, create_sample_image, get_image_methods
from PIL import Image, ImageDraw, ImageFont
import io
import random
import string
import base64
import traceback


def text_to_bits(text):
    """Convertit un texte en bits (chaîne de 0 et 1)."""
    return ''.join(format(ord(c), '08b') for c in text)


def bits_to_text(bits):
    """Convertit une chaîne binaire en texte (8 bits = 1 caractère)."""
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(b, 2)) for b in chars)


def decode_message_from_text(stego_text, bit_length):
    """Extrait les bits selon la casse, puis reconvertit en texte."""
    bits = []
    for c in stego_text:
        if c.isalpha():
            bits.append('1' if c.isupper() else '0')
        if len(bits) >= bit_length:
            break
    return bits_to_text(''.join(bits))


def build_paper_style_case(cover_text, secret_message, stego_text, bit_placements, bits):
    """Construit la représentation "papier" (string) pour la méthode 'case'."""
    lines = []
    lines.append('===== ÉTAPES DÉTAILLÉES =====')
    lines.append(f"Message à cacher : {secret_message}")
    lines.append(f"Nombre de caractères : {len(secret_message)}")
    lines.append(f"Bits ({len(bits)}) : {bits}")
    total_letters = sum(1 for c in cover_text if c.isalpha())
    lines.append(f"Emplacements alphabétiques disponibles : {total_letters}\n")
    lines.append('Conversion caractère → bits :')
    byte_groups = [bits[i:i+8] for i in range(0, len(bits), 8)]
    for ch, b in zip(secret_message, byte_groups):
        lines.append(f"  '{ch}' → {b}")

    lines.append('\nEncodage bit par bit :')
    lines.append('----------------------')
    for i, bp in enumerate(bit_placements, start=1):
        orig = bp.get('original_char', '')
        tr = bp.get('transformed', '')
        bit = bp.get('bit', '')
        lines.append(f"{i:02d}. Lettre '{orig}' → bit={bit} → '{tr}'")

    lines.append('----------------------')
    lines.append(f"Bits utilisés : {len(bit_placements)}/{len(bits)}")
    lines.append('Texte final après masquage :\n')
    excerpt = stego_text[:800]
    lines.append(excerpt)

    lines.append('\n==============================')
    lines.append('=== Vérification du décodage ===')
    # decode for verification
    try:
        decoded = decode_message_from_text(stego_text, len(bits))
        extracted_bits = text_to_bits(decoded)
    except Exception:
        decoded = '<decoding failed>'
        extracted_bits = ''

    lines.append(f"Bits extraits : {extracted_bits}")
    lines.append(f"Message décodé : {decoded}")
    lines.append('==============================')

    return '\n'.join(lines)


def index(request):
    """Render the main frontend interface."""
    return render(request, 'crypto_lab/index.html')


def get_encryption_steps(algorithm, plaintext, key, encrypted_text):
    """
    Génère les étapes explicatives du chiffrement
    """
    steps = []
    key_info = key.copy() if key else {}
    
    try:
        if algorithm == 'caesar':
            shift = key.get('shift', 0)
            steps.append(f"Algorithme: Chiffrement de César avec décalage de {shift}")
            steps.append(f"Texte nettoyé: {plaintext.upper().replace(' ', '')}")
            steps.append(f"Pour chaque lettre, ajouter {shift} positions dans l'alphabet (modulo 26)")
            steps.append(f"Exemple: A (position 0) → {chr((0 + shift) % 26 + ord('A'))} (position {shift})")
            
        elif algorithm == 'affine':
            a = key.get('a', 1)
            b = key.get('b', 0)
            steps.append(f"Algorithme: Chiffrement affine avec a={a}, b={b}")
            steps.append(f"Formule: E(x) = ({a} × x + {b}) mod 26")
            steps.append(f"Texte nettoyé: {plaintext.upper().replace(' ', '')}")
            steps.append(f"Pour chaque lettre x, calculer ({a} × x + {b}) mod 26")
            steps.append(f"Exemple: A (x=0) → ({a}×0+{b}) mod 26 = {b} → {chr(b + ord('A'))}")
            
        elif algorithm == 'playfair':
            keyword = key.get('keyword', '')
            steps.append(f"Algorithme: Chiffrement Playfair avec mot-clé '{keyword}'")
            steps.append(f"Génération de la matrice 5×5 à partir du mot-clé")
            steps.append(f"Texte préparé: remplacement de J par I, ajout de X entre lettres doubles")
            steps.append(f"Chiffrement par paires de lettres selon les règles Playfair:")
            steps.append(f"  - Même ligne: décaler à droite")
            steps.append(f"  - Même colonne: décaler vers le bas")
            steps.append(f"  - Rectangle: échanger les colonnes")
            
        elif algorithm == 'hill':
            if 'matrix' in key:
                matrix = key['matrix']
                steps.append(f"Algorithme: Chiffrement de Hill avec matrice 2×2")
                steps.append(f"Matrice de chiffrement: {matrix}")
                if 'source_keyword' in key:
                    steps.append(f"Matrice générée depuis le mot-clé: {key['source_keyword']}")
                steps.append(f"Texte groupé par paires de lettres")
                steps.append(f"Chaque paire est multipliée par la matrice (modulo 26)")
                steps.append(f"Formule: C = K × P mod 26")
        
        return {
            'original_text': plaintext,
            'encrypted_text': encrypted_text,
            'algorithm': algorithm,
            'steps': steps,
            'key_info': key_info
        }
        
    except Exception as e:
        return {
            'original_text': plaintext,
            'encrypted_text': encrypted_text,
            'algorithm': algorithm,
            'steps': [f"Chiffrement effectué avec succès"],
            'key_info': key_info
        }


@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Post Only'},status = 405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Validation des champs obligatoires
    username = data.get('username')
    password = data.get('password')
    algorithm = data.get('algorithm')
    key_param = data.get('key_param') or data.get('key')
    
    if not username:
        return JsonResponse({'error': 'Le champ "username" est obligatoire'}, status=400)
    if not password:
        return JsonResponse({'error': 'Le champ "password" est obligatoire'}, status=400)
    if not algorithm:
        return JsonResponse({'error': 'Le champ "algorithm" est obligatoire'}, status=400)
    if not key_param:
        return JsonResponse({'error': 'Le champ "key_param" ou "key" est obligatoire'}, status=400)
    
    # Vérifier si l'utilisateur existe déjà
    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({
            'error': f'Un utilisateur avec le nom "{username}" existe déjà',
            'suggestion': 'Veuillez choisir un autre nom d\'utilisateur'
        }, status=409)
    
    # Normaliser le nom de l'algorithme
    algo_normalized = algorithm.lower()
    if algo_normalized == 'cesar':
        algo_normalized = 'caesar'
    elif algo_normalized == 'plaiyfair':
        algo_normalized = 'playfair'
    
    try:
        if algorithm.lower() == 'cesar':
            key = {"shift": int(key_param)}
        elif algorithm.lower() == 'affine':
            # Format: "a,b" ou "5,8"
            parts = key_param.split(',')
            if len(parts) != 2:
                return JsonResponse({
                    'error': 'Format de clé Affine invalide',
                    'expected': 'Format attendu: "a,b" (exemple: "5,8")'
                }, status=400)
            key = {"a": int(parts[0].strip()), "b": int(parts[1].strip())}
        elif algorithm.lower() in ['playfair', 'plaiyfair']:
            key = {"keyword": key_param.strip().upper()}
        elif algorithm.lower() == 'hill':
            # Supporter matrice JSON ou mot-clé
            import json as json_lib
            if key_param.startswith('['):
                # Format matrice: [[3,3],[2,5]]
                matrix = json_lib.loads(key_param)
                key = {"matrix": matrix}
            else:
                # Format mot-clé: convertir en matrice 2x2
                keyword = key_param.strip().upper()
                # Prendre les 4 premiers caractères uniques
                unique_chars = []
                for char in keyword:
                    if char.isalpha() and char not in unique_chars:
                        unique_chars.append(char)
                
                # Compléter avec l'alphabet si nécessaire
                if len(unique_chars) < 4:
                    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                        if char not in unique_chars:
                            unique_chars.append(char)
                        if len(unique_chars) >= 4:
                            break
                
                # Convertir en valeurs numériques (A=0, B=1, etc.)
                matrix = [
                    [ord(unique_chars[0]) - ord('A'), ord(unique_chars[1]) - ord('A')],
                    [ord(unique_chars[2]) - ord('A'), ord(unique_chars[3]) - ord('A')]
                ]
                key = {"matrix": matrix, "source_keyword": keyword}
        else:
            return JsonResponse({
                'error': f'Algorithme inconnu: {algorithm}',
                'available_algorithms': ['cesar', 'affine', 'playfair', 'hill']
            }, status=400)
        
        # Convertir les chiffres en lettres si le mot de passe contient des chiffres
        # Exemple: "123" -> "BCD" (0->A, 1->B, 2->C, etc.)
        password_to_encrypt = password
        if any(c.isdigit() for c in password):
            # Le mot de passe contient des chiffres, les convertir en lettres
            password_to_encrypt = ''.join([
                chr(ord('A') + int(c)) if c.isdigit() else c 
                for c in password
            ])
        
        # Chiffrer avec les étapes
        encrypted_pass = encrypt_with_algorithm(algo_normalized, password_to_encrypt, key)
        
        # Récupérer les étapes d'explication si disponibles
        encryption_steps = get_encryption_steps(algo_normalized, password_to_encrypt, key, encrypted_pass)
        
    except ValueError as e:
        return JsonResponse({
            'error': 'Erreur de format de clé',
            'details': str(e),
            'hint': 'Vérifiez que la clé est au bon format pour l\'algorithme choisi'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Erreur lors du chiffrement',
            'details': str(e)
        }, status=400)
    
    try:
        user = CustomUser.objects.create(
            username=username,
            password_encypted=encrypted_pass,
            algorithm=algorithm,
            key_data=key
        )
    except Exception as e:
        return JsonResponse({
            'error': 'Erreur lors de la création de l\'utilisateur',
            'details': str(e)
        }, status=500)
    
    return JsonResponse({
        'message': f'User {username} registered successfully!',
        'encrypted_password': encrypted_pass,
        'encryption_steps': encryption_steps
    })        

@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Post Only'},status = 405)
    data = json.loads(request.body)
    username = data.get('username')
    password_input = data.get('password')
    captcha_value = data.get('captcha')

    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return JsonResponse({'message': 'User Not Found'}, status=404)
    
    # Vérifier si le compte est verrouillé
    if user.is_account_locked():
        remaining_minutes = user.get_lock_remaining_time()
        return JsonResponse({
            'error': 'Compte verrouillé',
            'message': f'Votre compte est verrouillé pour {remaining_minutes} minute(s) suite à trop de tentatives échouées.',
            'locked': True,
            'remaining_minutes': remaining_minutes
        }, status=403)
    
    # Si la protection est activée, exiger un CAPTCHA correct
    if user.protection_enabled:
        expected = request.session.get('captcha_code')
        if not captcha_value or not expected or str(captcha_value).strip().upper() != str(expected).upper():
            return JsonResponse({
                'error': 'CAPTCHA requis ou incorrect',
                'captcha_required': True
            }, status=400)

    # Parser la clé stockée selon l'algorithme
    try:
        algorithm = user.algorithm.lower()
        key = user.key_data  # key_data est déjà un dict (JSONField)
        
        # Normaliser le nom de l'algorithme
        algo_normalized = algorithm
        if algo_normalized == 'cesar':
            algo_normalized = 'caesar'
        elif algo_normalized == 'plaiyfair':
            algo_normalized = 'playfair'
        
        decrypted_pass = decrypt_with_algorithm(algo_normalized, user.password_encypted, key)
    except Exception as e:
        return JsonResponse({'error': f'Erreur de déchiffrement: {str(e)}'}, status=400)
    
    # Convertir le mot de passe saisi si il contient des chiffres (comme lors de l'enregistrement)
    password_to_check = password_input.upper().replace(" ", "")
    if any(c.isdigit() for c in password_to_check):
        password_to_check = ''.join([
            chr(ord('A') + int(c)) if c.isdigit() else c 
            for c in password_to_check
        ])
    
    if decrypted_pass == password_to_check:
        # Connexion réussie - réinitialiser les tentatives échouées
        user.reset_failed_attempts()
        # Invalider le captcha une fois utilisé
        if 'captcha_code' in request.session:
            try:
                del request.session['captcha_code']
            except Exception:
                pass
        return JsonResponse({
            'message': f'Welcome back {username}!',
            'username': username,
            'algorithm': user.algorithm,
            'success': True,
            'protection_enabled': user.protection_enabled
        })
    else:
        # Mot de passe incorrect - enregistrer la tentative échouée
        user.record_failed_attempt()
        
        # Préparer le message d'erreur
        error_message = 'Incorrect Password'
        if user.protection_enabled:
            attempts_left = max(0, 3 - user.failed_login_attempts)
            if attempts_left > 0:
                error_message = f'Mot de passe incorrect. Il vous reste {attempts_left} tentative(s).'
            else:
                error_message = 'Compte verrouillé pour 30 minutes suite à trop de tentatives échouées.'
        
        return JsonResponse({
            'error': error_message,
            'attempts_left': max(0, 3 - user.failed_login_attempts) if user.protection_enabled else None
        }, status=401)


def alpha_candidate(pt):
    p = ''.join(ch for ch in pt if ch.isalph())   
    return len(p) >= 3


@csrf_exempt
def api_get_user(request, username):
    """Return user record JSON for testing (safe: only returns stored encrypted blob and metadata)."""
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    return JsonResponse({
        'username': user.username,
        'password_encrypted': getattr(user, 'password_encrypted', None) or getattr(user, 'password_encypted', None),
        'algorithm': user.algorithm,
        'key_data': user.key_data,
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def api_attack_full_bruteforce(request):
    """Accepts the JSON instruction payload (as specified) and runs the attack runner.
    The attack runner enforces safety rules (test users only) and returns the structured report.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Vérifier la protection du compte ciblé
    target_username = payload.get('target_username')
    user_obj = None
    protection_enabled = False
    
    if target_username:
        try:
            user_obj = CustomUser.objects.get(username=target_username)
            protection_enabled = user_obj.protection_enabled
            
            # Vérifier si le compte est verrouillé
            if user_obj.is_account_locked():
                remaining_minutes = user_obj.get_lock_remaining_time()
                return JsonResponse({
                    'error': 'Compte verrouillé',
                    'message': f'Le compte {target_username} est verrouillé pour {remaining_minutes} minute(s) suite à trop de tentatives échouées.',
                    'locked': True,
                    'remaining_minutes': remaining_minutes,
                    'attempts_left': 0,
                    'matches_count': 0
                }, status=403)
        except CustomUser.DoesNotExist:
            pass  # Laisser l'attaque se poursuivre, elle échouera avec "User not found"

    # force mode to bruteforce
    payload['mode'] = 'bruteforce'
    report = run_attack(payload)
    
    # Si la protection est activée et l'attaque a échoué, incrémenter le compteur
    if protection_enabled and user_obj and report.get('matches_count', 0) == 0:
        user_obj.record_failed_attempt()
        attempts_left = max(0, 3 - user_obj.failed_login_attempts)
        
        # Ajouter l'info dans le rapport
        report['protection_active'] = True
        report['failed_attempts'] = user_obj.failed_login_attempts
        report['attempts_left'] = attempts_left
        
        if user_obj.is_account_locked():
            report['account_locked'] = True
            report['locked_message'] = 'Compte verrouillé pour 30 minutes suite à trop de tentatives échouées.'
        elif attempts_left > 0:
            report['warning'] = f'Attention : Il vous reste {attempts_left} tentative(s) avant le verrouillage du compte.'
    
    return JsonResponse(report, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def api_attack_full_dictionary(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Vérifier la protection du compte ciblé
    target_username = payload.get('target_username')
    user_obj = None
    protection_enabled = False
    
    if target_username:
        try:
            user_obj = CustomUser.objects.get(username=target_username)
            protection_enabled = user_obj.protection_enabled
            
            # Vérifier si le compte est verrouillé
            if user_obj.is_account_locked():
                remaining_minutes = user_obj.get_lock_remaining_time()
                return JsonResponse({
                    'error': 'Compte verrouillé',
                    'message': f'Le compte {target_username} est verrouillé pour {remaining_minutes} minute(s) suite à trop de tentatives échouées.',
                    'locked': True,
                    'remaining_minutes': remaining_minutes,
                    'attempts_left': 0,
                    'matches_count': 0
                }, status=403)
        except CustomUser.DoesNotExist:
            pass  # Laisser l'attaque se poursuivre, elle échouera avec "User not found"
    
    # Charger le dictionnaire depuis le fichier
    import os
    
    # Permettre de spécifier quel dictionnaire utiliser
    dict_type = payload.get('dictionary_type', 'default')  # 'default', '012', 'digits3', 'digits6', 'test'
    
    # Déterminer le chemin du dictionnaire
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    if dict_type == '012':
        dict_path = os.path.join(base_dir, 'backend', 'dictionaries', 'dict_012.txt')
    elif dict_type == 'digits3':
        dict_path = os.path.join(base_dir, 'backend', 'dictionaries', 'dict_digits3.txt')
    elif dict_type == 'digits6':
        dict_path = os.path.join(base_dir, 'backend', 'dictionaries', 'dict_digits6.txt')
    elif dict_type == 'test':
        dict_path = os.path.join(base_dir, 'backend', 'dictionaries', 'dict_test.txt')
    else:
        # Par défaut, utiliser backend/dic.txt
        dict_path = os.path.join(base_dir, 'backend', 'dic.txt')
    
    dictionary = []
    
    if os.path.exists(dict_path):
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                dictionary = [line.strip() for line in f if line.strip()]
        except Exception as e:
            return JsonResponse({'error': f'Erreur lecture dictionnaire: {str(e)}'}, status=500)
    else:
        return JsonResponse({
            'error': f'Fichier dictionnaire introuvable: {dict_path}',
            'suggestion': 'Exécutez: python generate_dictionaries.py'
        }, status=404)
    
    # Ajouter le dictionnaire au payload
    payload['mode'] = 'dictionary'
    payload['dictionary'] = dictionary
    
    # Ajouter des métadonnées sur le dictionnaire utilisé
    result = run_attack(payload)
    result['dictionary_info'] = {
        'type': dict_type,
        'path': dict_path,
        'size': len(dictionary)
    }
    
    # Si la protection est activée et l'attaque a échoué, incrémenter le compteur
    if protection_enabled and user_obj and result.get('matches_count', 0) == 0:
        user_obj.record_failed_attempt()
        attempts_left = max(0, 3 - user_obj.failed_login_attempts)
        
        # Ajouter l'info dans le rapport
        result['protection_active'] = True
        result['failed_attempts'] = user_obj.failed_login_attempts
        result['attempts_left'] = attempts_left
        
        if user_obj.is_account_locked():
            result['account_locked'] = True
            result['locked_message'] = 'Compte verrouillé pour 30 minutes suite à trop de tentatives échouées.'
        elif attempts_left > 0:
            result['warning'] = f'Attention : Il vous reste {attempts_left} tentative(s) avant le verrouillage du compte.'
    
    return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

def is_invertible_mod26(a):
    from math import gcd as math_gcd 
    return math_gcd(a,26) == 1

#--------------------BRUT FORCE----------------------------
@csrf_exempt
def full_brutforce(request):
    '''
    post -> json format 
    f(username,algorithm) -> to get encrypted pass from db 
    limit , maxsec, keyspace or dictionary => playfair 
    '''
        
    if request.methode != "POST":
        return JsonResponse({'error':'Post Only'},status = 405)

    payload = json.loads(request.body)
    username = payload.get('username')
    algo = payload.get('algo')
    limit =int(payload.get('limit',0))
    max_sec =float(payload.get('max_sec'))
    keyspace = payload.get('keyspace')

    try :
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist: 
        return JsonResponse({'message':'User Not Found'},status =404)
    
    encrypted = user.password_encypted #attacker shoold know the key ???? 
    start = time.perf_counter()
    attampts = 0 
    match = []



    # ---------- CAESAR ----------
    if algo == 'caesar':
        for s in range(26):
            attempts += 1
            guess = caesar_decrypt(encrypted, s)  # decrypt with shift s
            if alpha_candidate(guess):
                matches.append({'key': {'shift': s}, 'plaintext': guess})
            # limits
            if limit and attempts >= limit: break
            if max_seconds and (time.perf_counter() - start) > max_seconds: break

    # ---------- AFFINE ----------
    elif algo == 'affine':
        # a must be coprime with 26 (there are 12 such values)
        for a in range(1, 26):
            if gcd(a, 26) != 1:
                continue
            for b in range(26):
                attempts += 1
                try:
                    guess = affine_decrypt(encrypted, a, b)
                except Exception:
                    continue
                if alpha_candidate(guess):
                    matches.append({'key': {'a': a, 'b': b}, 'plaintext': guess})
                if limit and attempts >= limit: break
                if max_seconds and (time.perf_counter() - start) > max_seconds: break
            if limit and attempts >= limit: break
            if max_seconds and (time.perf_counter() - start) > max_seconds: break

    # ---------- PLAYFAIR ----------
    elif algo == 'playfair':
        # Brute-force Playfair by trying keys from provided keyspace (recommended).
        # Generating all 5-letter permutations (26P5) is infeasible — user should pass keyspace.
        if not keyspace:
            return JsonResponse({
                'error': 'Playfair brute-force requires "keyspace" (list of candidate keywords). Generating full keyspace is infeasible.'
            }, status=400)
        for k in keyspace:
            attempts += 1
            try:
                guess = playfair_decrypt(encrypted, k)
            except Exception:
                # key may be malformed but playfair_decrypt should generally work
                continue
            if alpha_candidate(guess):
                matches.append({'key': {'keyword': k}, 'plaintext': guess})
            if limit and attempts >= limit: break
            if max_seconds and (time.perf_counter() - start) > max_seconds: break

    # ---------- HILL 2x2 ----------
    elif algo == 'hill':
        # key is a 2x2 matrix of integers 0..25. We'll brute force all matrices with invertible det.
        # Total combos: 26^4 = 456,976 -> feasible but may take time.
        # We will iterate a,b,c,d in 0..25 and test invertibility (gcd(det,26)==1).
        for a in range(26):
            for b in range(26):
                for c in range(26):
                    for d in range(26):
                        attempts += 1
                        det = (a * d - b * c) % 26
                        # check invertible
                        from math import gcd as math_gcd
                        if math_gcd(det, 26) != 1:
                            # not invertible -> skip
                            pass
                        else:
                            key_mat = [[a, b], [c, d]]
                            try:
                                guess = hill_decrypt(encrypted, key_mat)
                            except Exception:
                                # if any error (shouldn't) skip
                                continue
                            if alpha_candidate(guess):
                                matches.append({'key': {'matrix': key_mat}, 'plaintext': guess})
                        # limits / timeout
                        if limit and attempts >= limit: break
                        if max_seconds and (time.perf_counter() - start) > max_seconds: break
                    if limit and attempts >= limit: break
                    if max_seconds and (time.perf_counter() - start) > max_seconds: break
                if limit and attempts >= limit: break
                if max_seconds and (time.perf_counter() - start) > max_seconds: break
            if limit and attempts >= limit: break
            if max_seconds and (time.perf_counter() - start) > max_seconds: break

    else:
        return JsonResponse({'error': 'Unsupported algorithm for brute-force'}, status=400)

    elapsed = time.perf_counter() - start

    # compact the matches to avoid returning enormous payloads if too many:
    max_results_return = 200
    total_matches = len(matches)
    if total_matches > max_results_return:
        excerpt = matches[:max_results_return]
        truncated = True
    else:
        excerpt = matches
        truncated = False

    return JsonResponse({
        'algorithm': algo,
        'username': username,
        'attempts': attempts,
        'time_sec': round(elapsed, 6),
        'matches_count': total_matches,
        'matches': excerpt,
        'truncated': truncated,
        'note': 'For Playfair supply "keyspace" list. For Hill full space is 26^4 (~456k). Use "limit" or "max_seconds" to bound the search.'
    }, json_dumps_params={'ensure_ascii': False})


# ============================================================================
# PASSWORD COMPLEXITY ANALYSIS ENDPOINTS (Partie 3)
# ============================================================================

@csrf_exempt
def api_password_complexity_analysis(request):
    """
    Analyse théorique de la complexité des 3 cas de mots de passe
    GET /api/analysis/complexity/
    """
    from backend.cryptotoolbox.attack.password_complexity import PasswordComplexityAnalyzer
    
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed. Use GET.'}, status=405)
    
    try:
        analyzer = PasswordComplexityAnalyzer()
        report = analyzer.generate_comprehensive_report()
        
        return JsonResponse(report, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_practical_attack(request):
    """
    Attaque pratique avec mesure du temps réel
    POST /api/analysis/practical-attack/
    Body: {
        "case": 1|2|3,
        "target_password": "012" | "123456" | "aB3$9z",
        "max_attempts": 100000  (optionnel pour cas 3)
    }
    """
    from backend.cryptotoolbox.attack.password_complexity import PasswordComplexityAnalyzer
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)
    
    try:
        data = json.loads(request.body)
        case = data.get('case')
        target_password = data.get('target_password')
        max_attempts = data.get('max_attempts')
        
        if not case or not target_password:
            return JsonResponse({
                'error': 'Missing required fields: case, target_password'
            }, status=400)
        
        analyzer = PasswordComplexityAnalyzer()
        
        if case == 1:
            result = analyzer.run_practical_attack_case_1(target_password)
        elif case == 2:
            result = analyzer.run_practical_attack_case_2(target_password, max_attempts)
        elif case == 3:
            max_attempts = max_attempts or 100000
            result = analyzer.run_practical_attack_case_3(target_password, max_attempts)
        else:
            return JsonResponse({'error': 'Invalid case. Must be 1, 2, or 3.'}, status=400)
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_protection_recommendations(request):
    """
    Recommandations de protection contre les attaques
    GET /api/analysis/protection-recommendations/
    """
    from backend.cryptotoolbox.attack.password_complexity import PasswordComplexityAnalyzer
    
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed. Use GET.'}, status=405)
    
    try:
        analyzer = PasswordComplexityAnalyzer()
        recommendations = analyzer.get_protection_recommendations()
        
        return JsonResponse(recommendations, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def generate_all_combinations_with_encryption(request):
    """
    Génère TOUTES les combinaisons possibles pour chaque cas
    avec les étapes de chiffrement détaillées
    
    CAS 1: {0,1,2} longueur 3 = 27 combinaisons
    CAS 2: {0-9} longueur 6 = 1,000,000 combinaisons (limité à 100 pour démo)
    CAS 3: {a-z,A-Z,0-9} longueur 6 = énorme (limité à 100 pour démo)
    """
    import itertools
    import string as str_module
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)
    
    try:
        data = json.loads(request.body)
        case_number = data.get('case', 1)  # 1, 2, ou 3
        algorithm = data.get('algorithm', 'cesar')  # Algorithme de chiffrement
        key_param = data.get('key_param', '3')  # Clé de chiffrement
        max_results = data.get('max_results', 100)  # Limite de résultats
        
        results = {
            'case': case_number,
            'algorithm': algorithm,
            'total_generated': 0,
            'combinations': []
        }
        
        # Définir le charset et la longueur selon le cas
        if case_number == 1:
            charset = ['0', '1', '2']
            length = 3
            max_results = 27  # Toutes les combinaisons (petit nombre)
            results['description'] = "Cas 1: 3 caractères, charset {0,1,2}"
            results['total_possible'] = 3 ** 3
            
        elif case_number == 2:
            charset = list(str_module.digits)  # 0-9
            length = 6
            results['description'] = "Cas 2: 6 caractères, charset {0-9}"
            results['total_possible'] = 10 ** 6
            
        elif case_number == 3:
            charset = list(str_module.ascii_lowercase + str_module.ascii_uppercase + str_module.digits)
            length = 6
            results['description'] = "Cas 3: 6 caractères, charset {a-z,A-Z,0-9}"
            results['total_possible'] = 62 ** 6
        else:
            return JsonResponse({'error': 'Case must be 1, 2, or 3'}, status=400)
        
        results['charset'] = ''.join(charset)
        results['charset_size'] = len(charset)
        results['password_length'] = length
        
        # Préparer la clé pour l'algorithme
        key = None
        if algorithm.lower() == 'cesar':
            key = {"shift": int(key_param)}
        elif algorithm.lower() == 'affine':
            parts = key_param.split(',')
            key = {"a": int(parts[0]), "b": int(parts[1])}
        elif algorithm.lower() == 'plaiyfair':
            key = {"keyword": key_param.upper()}
        elif algorithm.lower() == 'hill':
            if key_param.startswith('['):
                matrix = json.loads(key_param)
                key = {"matrix": matrix}
            else:
                # Conversion texte vers matrice
                keyword = key_param.strip().upper()
                unique_chars = []
                for char in keyword:
                    if char.isalpha() and char not in unique_chars:
                        unique_chars.append(char)
                
                def char_to_num(c):
                    return ord(c) - ord('A')
                
                if len(unique_chars) >= 4:
                    matrix = [
                        [char_to_num(unique_chars[0]), char_to_num(unique_chars[1])],
                        [char_to_num(unique_chars[2]), char_to_num(unique_chars[3])]
                    ]
                else:
                    matrix = [[3, 3], [2, 5]]
                
                key = {"matrix": matrix, "source_keyword": keyword}
        
        # Générer les combinaisons
        count = 0
        for combination in itertools.product(charset, repeat=length):
            if count >= max_results:
                break
            
            password = ''.join(combination)
            
            # Convertir les caractères en lettres si nécessaire pour le chiffrement
            # 0->A, 1->B, 2->C, etc.
            password_for_encryption = password
            if case_number in [1, 2]:  # Cas avec chiffres
                # Mapper chiffres vers lettres: 0->A, 1->B, ..., 9->J
                digit_to_letter = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'E',
                                  '5': 'F', '6': 'G', '7': 'H', '8': 'I', '9': 'J'}
                password_for_encryption = ''.join(digit_to_letter.get(c, c) for c in password)
            
            # Chiffrer le mot de passe
            try:
                encrypted = encrypt_with_algorithm(algorithm, password_for_encryption, key)
                
                # Obtenir les étapes de chiffrement
                encryption_steps = get_encryption_steps(algorithm, password_for_encryption, key, encrypted)
                
                results['combinations'].append({
                    'index': count + 1,
                    'plaintext_original': password,  # Combinaison originale (ex: "012")
                    'plaintext_converted': password_for_encryption,  # Converti pour chiffrement (ex: "ABC")
                    'encrypted': encrypted,
                    'steps': encryption_steps['steps'],
                    'key_info': encryption_steps['key_info']
                })
                
            except Exception as encrypt_error:
                results['combinations'].append({
                    'index': count + 1,
                    'plaintext_original': password,
                    'plaintext_converted': password_for_encryption,
                    'encrypted': 'ERROR',
                    'error': str(encrypt_error),
                    'steps': [],
                    'key_info': {}
                })
            
            count += 1
        
        results['total_generated'] = count
        results['showing_all'] = (count == results['total_possible'])
        
        if not results['showing_all']:
            results['note'] = f"Affichage limité à {max_results} résultats sur {results['total_possible']:,} possibles"
        
        return JsonResponse(results, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
def api_password_analysis(request):
    """
    API endpoint for password complexity analysis and attack simulation.
    
    POST /api/password-analysis/
    
    Request body:
    {
        "case_id": "case1" | "case2" | "case3",
        "password": "optional_test_password"
    }
    
    Returns:
    - Case information (charset, length, keyspace)
    - Brute-force attack results with timing
    - Dictionary attack results with timing
    - Estimated time for full keyspace search
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)
    
    try:
        from backend.cryptotoolbox.attack.password_analysis import analyze_password_case
        
        data = json.loads(request.body)
        case_id = data.get('case_id')
        password = data.get('password')
        
        if not case_id:
            return JsonResponse({'error': 'case_id is required (case1, case2, or case3)'}, status=400)
        
        result = analyze_password_case(case_id, password)
        
        if 'error' in result:
            return JsonResponse(result, status=400)
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
def api_password_cases_info(request):
    """
    API endpoint to get information about all password complexity cases.
    
    GET /api/password-cases-info/
    
    Returns:
    - Information about all three password cases
    - Charset, length, and keyspace for each
    """
    try:
        from backend.cryptotoolbox.attack.password_analysis import get_all_cases_info
        
        info = get_all_cases_info()
        return JsonResponse(info, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
def api_toggle_protection(request, username):
    """
    API endpoint to toggle account protection.
    
    POST /api/users/<username>/toggle-protection/
    Body: { "enabled": true/false }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        enabled = data.get('enabled', not user.protection_enabled)
        
        user.protection_enabled = enabled
        
        # Si on désactive la protection, réinitialiser les tentatives
        if not enabled:
            user.failed_login_attempts = 0
            user.account_locked_until = None
            user.last_failed_attempt = None
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'username': username,
            'protection_enabled': user.protection_enabled,
            'message': f'Protection {"activée" if enabled else "désactivée"} pour {username}'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_get_protection_status(request, username):
    """
    API endpoint to get protection status.
    
    GET /api/users/<username>/protection-status/
    """
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    return JsonResponse({
        'username': username,
        'protection_enabled': user.protection_enabled,
        'failed_attempts': user.failed_login_attempts,
        'is_locked': user.is_account_locked(),
        'remaining_minutes': user.get_lock_remaining_time() if user.is_account_locked() else 0,
        'last_failed_attempt': user.last_failed_attempt.isoformat() if user.last_failed_attempt else None
    })


@csrf_exempt
def api_unlock_account(request, username):
    """
    API endpoint to manually unlock an account (admin function).
    
    POST /api/users/<username>/unlock/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    user.reset_failed_attempts()
    
    return JsonResponse({
        'success': True,
        'username': username,
        'message': f'Compte {username} déverrouillé avec succès'
    })


@csrf_exempt
def api_password_protection_recommendations(request):
    """
    API endpoint to get password protection recommendations.
    
    GET /api/password-protection/
    
    Returns:
    - Comprehensive security recommendations
    - Best practices for password hashing
    - Protection strategies against attacks
    - Comparison of password strengths
    """
    try:
        from backend.cryptotoolbox.attack.password_analysis import get_protection_recommendations
        
        recommendations = get_protection_recommendations()
        return JsonResponse(recommendations, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# ==================== STEGANOGRAPHY ENDPOINTS ====================

@csrf_exempt
def api_text_stego_hide(request):
    """
    Cache un message secret dans un texte de couverture
    
    POST /api/stego/text/hide/
    Body: {
        "cover_text": "Le texte visible qui servira de couverture...",
        "secret_message": "Message secret",
        "method": "whitespace" | "zerowidth" | "case"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        cover_text = data.get('cover_text')
        secret_message = data.get('secret_message')
        method = data.get('method', 'whitespace')
        
        if not cover_text or not secret_message:
            return JsonResponse({
                'error': 'cover_text et secret_message sont requis'
            }, status=400)
        
        result = hide_text_in_text(cover_text, secret_message, method)

        # Détails pédagogiques: étapes et limites (comme une solution sur papier)
        details = {
            'method': method,
            'steps': [],
            'capacity_estimate': None,
            'notes': []
        }

        # Estimer la capacité (nombre d'emplacements simples: espaces + retours)
        spaces = cover_text.count(' ')
        newlines = cover_text.count('\n')
        rough_slots = spaces + newlines
        details['capacity_estimate'] = {
            'available_slots': rough_slots,
            'message_length_chars': len(secret_message),
            'message_length_bytes': len(secret_message.encode('utf-8'))
        }

        # Calcul plus détaillé de capacité en bits/bytes selon méthode
        if method == 'whitespace' or method == 'case':
            # Ces méthodes utilisent typiquement 1 bit par emplacement (espace ou lettre)
            details['capacity_bits'] = rough_slots
            details['capacity_bytes'] = rough_slots // 8
            details['capacity_calculation'] = '1 bit per usable slot (space or letter).'
        elif method == 'zerowidth':
            # Zero-width can be inserted between characters
            details['capacity_bits'] = len(cover_text)
            details['capacity_bytes'] = len(cover_text) // 8
            details['capacity_calculation'] = '1 bit per possible insertion point (between characters).'

        # Exemple de conversion du message en bits (UTF-8) pour expliquer comment encoder
        try:
            msg_bytes = secret_message.encode('utf-8')
            bits_example = ''.join(f"{b:08b}" for b in msg_bytes)
            details['conversion'] = {
                'message_bytes': list(msg_bytes),
                'bits': bits_example,
                'note': 'Use UTF-8 encoding. Optionally prefix the message with a fixed-size length field (e.g. 32 bits) to know when to stop during extraction.'
            }
        except Exception:
            details['conversion'] = {'error': 'Failed to convert message to bytes for example.'}

        # Stratégies pour choisir les emplacements (important pour robustesse/répétabilité)
        details['placement_strategies'] = [
            {
                'name': 'sequential',
                'description': 'Use the first N available slots in left-to-right order. Simple and deterministic.'
            },
            {
                'name': 'pseudo-random',
                'description': 'Use a PRNG with a known seed (shared secret) to pick slot indices. More stealthy, requires the same seed for extraction.'
            },
            {
                'name': 'key-derived',
                'description': 'Derive positions from a cryptographic key or hash (e.g. HMAC) to make placement dependent on a password/key.'
            }
        ]
        details['recommended'] = 'For teaching/demos use sequential. For real use, prefer pseudo-random or key-derived plus a length prefix.'

        if method == 'whitespace':
            details['steps'] = [
                '1) Convertir le message secret en bits (UTF-8).',
                "2) Choisir une règle d'encodage: par exemple, 'absence d'espace' = bit 0, 'espace double' = bit 1, ou espace simple/fin de ligne comme délimiteurs.",
                '3) Parcourir le texte de couverture et appliquer la règle aux emplacements choisis (espaces ou fins de ligne).',
                '4) Pour l’extraction, lire les emplacements dans le même ordre et reconstruire la suite de bits puis la chaîne UTF-8.'
            ]
            details['notes'].append('Très sensible aux opérations de normalisation du texte (trim, collapse spaces).')
            details['notes'].append('Capacité approximative = nombre d’espaces/retours utilisables.')

        elif method == 'zerowidth':
            details['steps'] = [
                '1) Convertir le message secret en bits (UTF-8).',
                "2) Choisir un mapping: par exemple U+200B = '0', U+200C = '1'.",
                '3) Insérer les caractères zero-width entre caractères/mots du texte de couverture selon l’ordre des bits.',
                '4) Extraction: détecter et lire la séquence de zero-width, reconstruire les bits et décoder en UTF-8.'
            ]
            details['notes'].append('Invisible à l’œil, mais certains nettoyages/sanitizers HTML peuvent les supprimer.')

        elif method == 'case':
            details['steps'] = [
                '1) Convertir le message secret en bits.',
                "2) Pour chaque lettre alphabétique dans le texte de couverture: définir minuscule => bit 0, majuscule => bit 1 (ou l’inverse).",
                '3) Extraction: lire la casse des lettres dans le même ordre pour reconstruire les bits et décoder.'
            ]
            details['notes'].append('Modifie visuellement la casse des lettres; peut être altéré par normalisation (lower/upper).')

        else:
            details['steps'] = ['Méthode non standard: consultez la documentation.']

        # Ajouter les détails au résultat renvoyé
        if isinstance(result, dict):
            result.setdefault('details', {})
            result['details'].update(details)

        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_text_stego_extract(request):
    """
    Extrait un message secret d'un texte stéganographié
    
    POST /api/stego/text/extract/
    Body: {
        "stego_text": "Texte contenant un message caché",
        "method": "whitespace" | "zerowidth" | "case"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        stego_text = data.get('stego_text')
        method = data.get('method', 'whitespace')
        
        if not stego_text:
            return JsonResponse({
                'error': 'stego_text est requis'
            }, status=400)
        
        result = extract_text_from_text(stego_text, method)

        # Détails pédagogiques sur l'extraction
        details = {
            'method': method,
            'steps': [],
            'notes': []
        }

        # Fournir une explication détaillée de la conversion bits->message
        details['extraction_conversion'] = {
            'note': 'Lors de l’extraction, collectez la suite de bits dans l’ordre, groupez par 8 et décodez en UTF-8. Si le message a été précédé d’un préfixe longueur, utilisez-le pour arrêter la lecture.'
        }

        # Conseils pour détecter les emplacements choisis
        details['how_to_find_slots'] = {
            'whitespace': 'Scanner les espaces et compter les occurrences (simple vs double espace). Attention aux collapses d’espaces par l’éditeur.',
            'zerowidth': 'Scanner pour U+200B/U+200C (ou le mapping choisi). Ces caractères sont invisibles dans l’affichage mais présents dans la chaîne.',
            'case': 'Parcourir uniquement les caractères alphabétiques et lire leur casse (upper/lower).'
        }

        # Exemples d'erreurs fréquentes
        details['error_modes'] = [
            'Normalisation du texte: trim/collapse/replace multiple spaces.',
            'Suppression de caractères zero-width par des sanitizeurs HTML.',
            'Changement automatique de casse (lower/upper) par traitement de texte.'
        ]

        if method == 'whitespace':
            details['steps'] = [
                '1) Scanner le texte de gauche à droite et collecter les emplacements d’espaces/fins de ligne.',
                '2) Interpréter la présence/absence ou le motif d’espacement selon la règle utilisée pour obtenir des bits.',
                '3) Grouper les bits par 8 et décoder en UTF-8 pour reconstituer le message.'
            ]
            details['notes'].append('Vérifier la normalisation appliquée par l’éditeur/transport (trim/collapse).')

        elif method == 'zerowidth':
            details['steps'] = [
                '1) Parcourir le texte et détecter les caractères zero-width aux positions attendues.',
                '2) Traduire chaque caractère zero-width en bit selon le mapping choisi (ex: U+200B -> 0, U+200C -> 1).',
                '3) Reconstituer les octets et décoder en UTF-8.'
            ]
            details['notes'].append('S’assurer que les zero-width n’ont pas été supprimés par un sanitizer.')

        elif method == 'case':
            details['steps'] = [
                '1) Parcourir les lettres alphabétiques du texte de couverture dans l’ordre.',
                "2) Interpréter la casse de chaque lettre comme bit 0/1 selon la convention utilisée.",
                '3) Grouper par octets et décoder.'
            ]
            details['notes'].append('La casse peut être modifiée par des transformations automatiques lors du transit.')

        else:
            details['steps'] = ['Méthode non standard: extraction dynamique.']

        if isinstance(result, dict):
            result.setdefault('details', {})
            result['details'].update(details)

        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_stego_text_show_steps(request):
    """
    Montre toutes les étapes pour cacher un message dans un texte (et la vérification inverse).

    POST /api/stego/text/show-steps/
    Body: { "cover_text": "...", "secret_message": "...", "method": "whitespace|zerowidth|case" }
    Retourne un tracé pas-à-pas: bits, positions, stego_text, étapes et tentative d'extraction.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json.loads(request.body)
        cover_text = data.get('cover_text')
        secret_message = data.get('secret_message')
        method = data.get('method', 'whitespace')

        if not cover_text or not secret_message:
            return JsonResponse({'error': 'cover_text and secret_message are required'}, status=400)

        # Convertir le message secret en bits (UTF-8)
        msg_bytes = secret_message.encode('utf-8')
        bits = ''.join(f"{b:08b}" for b in msg_bytes)

        trace = {
            'secret_message': secret_message,
            'message_bytes': list(msg_bytes),
            'bits': bits,
            'method': method,
            'used_slots': None,
            'stego_text': None,
            'notes': []
        }

        # Simuler l'encodage selon la méthode choisie
        if method == 'whitespace':
            # On n'utilise que les espaces ' ' comme emplacements (plus simple et reproductible)
            needed = len(bits)
            slots = [i for i, ch in enumerate(cover_text) if ch == ' ']
            trace['available_slots'] = len(slots)

            if len(slots) < needed:
                trace['notes'].append('Pas assez d’emplacements (espaces) dans le texte de couverture pour encoder tous les bits.')

            # Construire le texte résultat en itérant et consommant les bits lorsque l'on rencontre un espace
            out_chars = []
            bit_index = 0
            slot_counter = 0
            bit_placements = []
            for i, ch in enumerate(cover_text):
                # ajouter le caractère original
                out_chars.append(ch)
                if ch == ' ' and bit_index < len(bits):
                    b = bits[bit_index]
                    # règle: espace simple => bit 0 (laisser un espace), double espace => bit 1 (ajouter un espace supplémentaire)
                    if b == '1':
                        out_chars.append(' ')
                    # enregistrer l'emplacement et le bit
                    bit_placements.append({
                        'slot_index': slot_counter,
                        'char_index': i,
                        'bit': b,
                        'context': cover_text[max(0, i-10): i+10]
                    })
                    slot_counter += 1
                    bit_index += 1

            stego_text = ''.join(out_chars)
            trace['used_slots'] = bit_index
            trace['stego_text'] = stego_text
            trace['bit_placements'] = bit_placements
            trace['positions'] = [bp['char_index'] for bp in bit_placements]
            steps = [
                '1) Convertir le message en bits (UTF-8).',
                "2) Parcourir le texte de couverture et pour chaque espace disponible, écrire un bit: espace simple=0, double=1.",
                '3) Si il n’y a pas assez d’espaces, le message est tronqué ou il faut changer de méthode/texte de couverture.',
                '4) Pour l’extraction, lire chaque espace dans le même ordre et reconstruire les bits.'
            ]

        elif method == 'zerowidth':
            # mapping: U+200B -> 0, U+200C -> 1
            z0 = '\u200b'
            z1 = '\u200c'
            needed = len(bits)
            # positions possibles: after each character (between chars), count = len(cover_text)
            max_positions = len(cover_text)
            trace['available_slots'] = max_positions

            if max_positions < needed:
                trace['notes'].append('Pas assez d’emplacements (entre-caractères) pour encoder tous les bits.')

            out = []
            bit_index = 0
            for i, ch in enumerate(cover_text):
                out.append(ch)
                if bit_index < len(bits):
                    b = bits[bit_index]
                    zchar = z1 if b == '1' else z0
                    out.append(zchar)
                    # record placement after character i
                    if 'bit_placements' not in trace:
                        trace['bit_placements'] = []
                    trace['bit_placements'].append({'char_index': i, 'bit': b, 'mapping': '\\u200b=0 \\u200c=1'})
                    bit_index += 1

            stego_text = ''.join(out)
            trace['used_slots'] = bit_index
            trace['stego_text'] = stego_text
            steps = [
                '1) Convertir le message en bits (UTF-8).',
                '2) Choisir un mapping zero-width (ex: U+200B=0, U+200C=1).',
                '3) Insérer le caractère zero-width correspondant après chaque caractère du texte de couverture pour écrire les bits.',
                '4) Pour l’extraction, détecter les zero-width dans le texte et reconstruire les bits puis la chaîne UTF-8.'
            ]

        elif method == 'case':
            needed = len(bits)
            letters_indices = [i for i, ch in enumerate(cover_text) if ch.isalpha()]
            trace['available_slots'] = len(letters_indices)

            if len(letters_indices) < needed:
                trace['notes'].append('Pas assez de lettres alphabétiques dans le texte de couverture pour encoder tous les bits. Le message sera tronqué.')

            out_chars = list(cover_text)
            bit_index = 0
            bit_placements = []
            for slot_idx, idx in enumerate(letters_indices):
                if bit_index >= len(bits):
                    break
                b = bits[bit_index]
                ch = out_chars[idx]
                transformed = ch.upper() if b == '1' else ch.lower()
                out_chars[idx] = transformed
                # record placement with more detail
                bit_placements.append({
                    'slot_index': slot_idx + 1,
                    'char_index': idx,
                    'original_char': ch,
                    'bit': b,
                    'transformed': transformed
                })
                bit_index += 1

            stego_text = ''.join(out_chars)
            trace['used_slots'] = bit_index
            trace['stego_text'] = stego_text
            trace['bit_placements'] = bit_placements
            steps = [
                '1) Convertir le message en bits (UTF-8).',
                "2) Parcourir les lettres alphabétiques et définir majuscule=1/minuscule=0 pour écrire les bits.",
                '3) Pour l’extraction, lire la casse des lettres dans le même ordre et reconstruire la suite de bits.'
            ]

            # Build a human-readable, paper-style representation using helper
            try:
                trace['paper_style'] = build_paper_style_case(cover_text, secret_message, stego_text, bit_placements, bits)
            except Exception:
                trace.setdefault('notes', []).append('Failed to build paper-style representation')

        else:
            return JsonResponse({'error': f'Method {method} not supported for step-by-step demo'}, status=400)

        # Vérifier l'extraction via la fonction existante (si disponible)
        try:
            extracted = extract_text_from_text(trace['stego_text'], method)
        except Exception as e:
            extracted = {'error': f'Extraction simulation failed: {str(e)}'}

        response = {
            'success': True,
            'method': method,
            'steps': steps,
            'trace': trace,
            'extraction_simulation': extracted
        }

        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@csrf_exempt
def api_stego_text_extract_steps(request):
    """
    Montre pas-à-pas comment extraire un message d'un texte stéganographié.

    POST /api/stego/text/extract-steps/
    Body: { "stego_text": "...", "method": "whitespace|zerowidth|case" }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json.loads(request.body)
        stego_text = data.get('stego_text')
        method = data.get('method', 'whitespace')

        if not stego_text:
            return JsonResponse({'error': 'stego_text is required'}, status=400)

        steps = []
        trace = {'method': method}

        if method == 'whitespace':
            # lire les espaces
            bits = []
            for ch in stego_text:
                if ch == ' ':
                    # check if next char also space (double)
                    # this simple heuristic won't alter original but for demo we lookahead
                    # build by scanning with index
                    pass

            # Implement robust scan to detect single vs double spaces
            bits = []
            i = 0
            s = stego_text
            positions = []
            while i < len(s):
                if s[i] == ' ':
                    # if next char is also space -> '1'
                    if i + 1 < len(s) and s[i+1] == ' ':
                        bits.append('1')
                        positions.append(i)
                        # consume the double space by skipping the second
                        i += 2
                    else:
                        bits.append('0')
                        positions.append(i)
                        i += 1
                else:
                    i += 1

            bits_str = ''.join(bits)
            # regrouper en octets
            bytes_out = [int(bits_str[i:i+8], 2) for i in range(0, len(bits_str) - (len(bits_str)%8), 8)]
            try:
                decoded = bytes(bytes_out).decode('utf-8') if bytes_out else ''
            except Exception:
                decoded = '<non-decodable>'

            trace.update({'bits': bits_str, 'bytes': bytes_out, 'decoded': decoded})
            trace['positions'] = positions
            steps = [
                '1) Scanner le texte et repérer chaque emplacement d’espace.',
                "2) Détecter double espace => bit '1', espace simple => bit '0'.",
                '3) Grouper les bits par 8 et décoder en UTF-8.'
            ]

        elif method == 'zerowidth':
            z0 = '\u200b'
            z1 = '\u200c'
            bits = []
            i = 0
            s = stego_text
            positions = []
            while i < len(s):
                ch = s[i]
                i += 1
                # check following zero-width
                if i < len(s) and s[i] in (z0, z1):
                    bits.append('1' if s[i] == z1 else '0')
                    positions.append(i)
                    i += 1

            bits_str = ''.join(bits)
            bytes_out = [int(bits_str[i:i+8], 2) for i in range(0, len(bits_str) - (len(bits_str)%8), 8)]
            try:
                decoded = bytes(bytes_out).decode('utf-8') if bytes_out else ''
            except Exception:
                decoded = '<non-decodable>'

            trace.update({'bits': bits_str, 'bytes': bytes_out, 'decoded': decoded})
            trace['positions'] = positions
            steps = [
                '1) Parcourir le texte et détecter les caractères zero-width entre caractères.',
                '2) Traduire chaque zero-width en bit selon le mapping (ex: U+200B=0, U+200C=1).',
                '3) Grouper les bits par 8 et décoder en UTF-8.'
            ]

        elif method == 'case':
            bits = []
            positions = []
            for i, ch in enumerate(stego_text):
                if ch.isalpha():
                    bits.append('1' if ch.isupper() else '0')
                    positions.append(i)

            bits_str = ''.join(bits)
            bytes_out = [int(bits_str[i:i+8], 2) for i in range(0, len(bits_str) - (len(bits_str)%8), 8)]
            try:
                decoded = bytes(bytes_out).decode('utf-8') if bytes_out else ''
            except Exception:
                decoded = '<non-decodable>'

            trace.update({'bits': bits_str, 'bytes': bytes_out, 'decoded': decoded})
            trace['positions'] = positions
            steps = [
                '1) Parcourir les lettres alphabétiques dans l’ordre.',
                '2) Interpréter majuscule=1 / minuscule=0 pour chaque lettre.',
                '3) Grouper les bits par 8 et décoder en UTF-8.'
            ]

        else:
            return JsonResponse({'error': f'Method {method} not supported for extraction step demo'}, status=400)

        return JsonResponse({'success': True, 'method': method, 'steps': steps, 'trace': trace}, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@csrf_exempt
def api_image_stego_hide(request):
    """
    Cache un message secret dans une image
    
    POST /api/stego/image/hide/
    Body: {
        "image_data": "base64_encoded_image",
        "secret_message": "Message secret",
        "method": "lsb"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        image_data = data.get('image_data')
        secret_message = data.get('secret_message')
        method = data.get('method', 'lsb')
        auto_resize = bool(data.get('auto_resize', True))
        
        if not image_data or not secret_message:
            return JsonResponse({
                'error': 'image_data et secret_message sont requis'
            }, status=400)
        
        # Décoder l'image base64
        try:
            # Enlever le préfixe data:image/...;base64, si présent
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return JsonResponse({
                'error': f'Erreur de décodage base64: {str(e)}'
            }, status=400)

        # Garde-fous taille upload (octets)
        MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB
        if len(image_bytes) > MAX_UPLOAD_BYTES:
            return JsonResponse({
                'error': 'Image trop volumineuse',
                'details': f'Taille {len(image_bytes)//1024} KB > limite {MAX_UPLOAD_BYTES//1024} KB',
                'hint': 'Choisissez une image plus petite ou activez la réduction côté client'
            }, status=413)

        # Optionnel: redimensionner si trop grande pour éviter blocage mémoire/CPU
        resized_info = {}
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode not in ('RGB', 'RGBA'):  # normaliser pour la capacité
                img = img.convert('RGB')
            orig_w, orig_h = img.size
            max_dim = 2048
            max_pixels = 4_500_000  # ~4.5 MP
            if auto_resize and (orig_w > max_dim or orig_h > max_dim or (orig_w * orig_h) > max_pixels):
                # Conserver ratio
                img.thumbnail((max_dim, max_dim))
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                image_bytes = buf.getvalue()
                resized_info = {
                    'resized': True,
                    'original_size': f'{orig_w}x{orig_h}',
                    'new_size': f'{img.size[0]}x{img.size[1]}'
                }
            else:
                resized_info = {
                    'resized': False,
                    'original_size': f'{orig_w}x{orig_h}',
                    'new_size': f'{orig_w}x{orig_h}'
                }
        except Exception:
            # Si l’ouverture échoue, on continue et laisse hide_text_in_image gérer l’erreur
            pass
        
        result = hide_text_in_image(image_bytes, secret_message, method)

        # Calculer la capacité et fournir une explication pas-à-pas
        details = {
            'method': method,
            'steps': [],
            'capacity_bits': None,
            'capacity_bytes': None,
            'message_length_bytes': len(secret_message.encode('utf-8')),
            'notes': []
        }

        try:
            img_check = Image.open(io.BytesIO(image_bytes))
            mode = img_check.mode
            w, h = img_check.size
            # déterminer le nombre de canaux approximatif
            if mode == 'RGB':
                channels = 3
            elif mode == 'RGBA':
                channels = 4
            elif mode == 'L':
                channels = 1
            else:
                # heuristique: treat as RGB
                channels = 3

            capacity_bits = w * h * channels
            capacity_bytes = capacity_bits // 8

            details['capacity_bits'] = capacity_bits
            details['capacity_bytes'] = capacity_bytes

            details['steps'] = [
                '1) Convertir le message secret en bits (UTF-8).',
                '2) Optionnel: stocker la longueur du message dans un en-tête (p.ex. premiers pixels).',
                '3) Parcourir les pixels et, pour chaque canal choisi (R,G,B), remplacer le bit de poids faible (LSB) par un bit du message.',
                '4) Sauvegarder l’image résultante en format lossless (PNG) pour conserver les LSB.',
            ]

            details['notes'].append('Capacité approximative calculée depuis largeur×hauteur×canaux.')
            details['notes'].append('Ne pas utiliser JPEG (lossy) pour LSB, car la compression détruit les bits cachés.')

        except Exception as e:
            details['notes'].append(f"Impossible d'analyser l'image pour la capacité: {str(e)}")

        if isinstance(resized_info, dict) and resized_info:
            result.update(resized_info)

        if isinstance(result, dict):
            result.setdefault('details', {})
            result['details'].update(details)

        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
def api_image_stego_extract(request):
    """
    Extrait un message secret d'une image stéganographiée
    
    POST /api/stego/image/extract/
    Body: {
        "image_data": "base64_encoded_image",
        "method": "lsb"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        image_data = data.get('image_data')
        method = data.get('method', 'lsb')
        
        if not image_data:
            return JsonResponse({
                'error': 'image_data est requis'
            }, status=400)
        
        # Décoder l'image base64
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return JsonResponse({
                'error': f'Erreur de décodage base64: {str(e)}'
            }, status=400)

        # Garde-fous: refuser les images trop volumineuses pour extraction (on ne peut pas redimensionner sans perdre le message)
        MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB
        if len(image_bytes) > MAX_UPLOAD_BYTES:
            return JsonResponse({
                'error': 'Image trop volumineuse pour extraction',
                'details': f'Taille {len(image_bytes)//1024} KB > limite {MAX_UPLOAD_BYTES//1024} KB',
                'hint': 'Utilisez une image plus petite ou compressez-la sans perte avant l’intégration du message'
            }, status=413)

        # Vérifier rapidement la dimension en pixels
        try:
            img = Image.open(io.BytesIO(image_bytes))
            w, h = img.size
            max_pixels = 6_000_000  # ~6 MP
            if (w * h) > max_pixels:
                return JsonResponse({
                    'error': 'Image trop grande (dimensions)',
                    'details': f'{w}x{h} > limite de {max_pixels} pixels',
                    'hint': 'Réduisez la résolution avant l’extraction (sinon le message sera perdu)'
                }, status=413)
        except Exception:
            pass
        
        result = extract_text_from_image(image_bytes, method)

        # Détails pédagogiques sur l'extraction depuis l'image
        details = {
            'method': method,
            'steps': [],
            'capacity_bits': None,
            'capacity_bytes': None,
            'notes': []
        }

        try:
            img_check = Image.open(io.BytesIO(image_bytes))
            mode = img_check.mode
            w, h = img_check.size
            if mode == 'RGB':
                channels = 3
            elif mode == 'RGBA':
                channels = 4
            elif mode == 'L':
                channels = 1
            else:
                channels = 3

            capacity_bits = w * h * channels
            capacity_bytes = capacity_bits // 8

            details['capacity_bits'] = capacity_bits
            details['capacity_bytes'] = capacity_bytes

            details['steps'] = [
                '1) Lire l’en-tête si présent pour connaître la longueur du message.',
                '2) Parcourir les pixels dans le même ordre que l’insertion et récupérer les LSB des canaux utilisés.',
                '3) Reconstituer les octets à partir des bits récupérés et décoder en UTF-8.',
            ]

            details['notes'].append('Si l’image a subi une compression lossy, LSB peut être corrompu.')

        except Exception as e:
            details['notes'].append(f"Impossible d'analyser l'image pour la capacité: {str(e)}")

        if isinstance(result, dict):
            result.setdefault('details', {})
            result['details'].update(details)

        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
def api_stego_methods(request):
    """
    Retourne les méthodes de stéganographie disponibles
    
    GET /api/stego/methods/
    """
    # Enrichir la réponse avec des descriptions détaillées (comme une solution sur papier)
    text_methods = get_available_methods()
    image_methods = get_image_methods()

    # Descriptions humaines pour chaque méthode (breve puis détaillée)
    text_method_details = {}
    for m in text_methods:
        if m == 'whitespace':
            text_method_details[m] = {
                'short': 'Encodage par espaces/fins de ligne (whitespace)',
                'detailed_steps': [
                    '1) Convertir le message secret en bits (UTF-8).',
                    "2) Pour chaque bit, encoder '0' ou '1' en ajoutant ou non un espace supplémentaire à la fin d'une ligne ou d'un mot (ou en utilisant un motif d'espacement).",
                    "3) Le texte de couverture reste lisible: seul le motif d'espacement transporte l'information.",
                    '4) Limites: sensible au ré-encodage/normalisation du texte (trim, collapse spaces).',
                    '5) Capacités: dépend du nombre d’emplacements d’espaces/fins de ligne dans le texte de couverture.'
                ]
            }
        elif m == 'zerowidth':
            text_method_details[m] = {
                'short': 'Caractères invisibles (zero-width) insérés entre les caractères',
                'detailed_steps': [
                    '1) Convertir le message secret en bits (UTF-8).',
                    '2) Utiliser des caractères zero-width (U+200B, U+200C, U+200D, U+FEFF) pour représenter 0/1 ou des séquences de bits.',
                    '3) Insérer ces caractères entre lettres/mots du texte de couverture selon une règle définie.',
                    '4) Extraction: lire la séquence de zero-width et reconstruire les bits puis l’octet et enfin la chaîne UTF-8.',
                    '5) Avantages: invisible à l’œil, résiste mieux aux collapses d’espaces mais peut être supprimé par certains éditeurs/conversions (ex: nettoyage HTML).'
                ]
            }
        elif m == 'case':
            text_method_details[m] = {
                'short': 'Encodage par casse (majuscules/minuscules)',
                'detailed_steps': [
                    '1) Convertir le message secret en bits.',
                    "2) Parcourir les caractères alphabétiques du texte de couverture et définir: lettre en minuscule => bit '0', lettre en majuscule => bit '1'.",
                    '3) Extraction: lire la casse des lettres selon la même règle et reconstruire le message.',
                    '4) Limites: modifie la lisibilité (esthétique) et peut être altéré par normalisation qui change la casse.'
                ]
            }
        else:
            text_method_details[m] = {'short': m, 'detailed_steps': ['Méthode connue, détails non spécifiés.']}

    image_method_details = {}
    for m in image_methods:
        if m == 'lsb':
            image_method_details[m] = {
                'short': 'Least Significant Bit (LSB) - insertion dans les bits de couleur',
                'detailed_steps': [
                    '1) Convertir le message secret en une suite de bits (UTF-8).',
                    '2) Ouvrir l’image en mode RGB (3 canaux) ou RGBA.',
                    '3) Pour chaque pixel et pour chaque canal (R,G,B), remplacer le bit le moins significatif par un bit du message.',
                    "4) Continuer jusqu'à épuisement des bits du message; stocker la longueur du message en en-tête (par ex. dans les premiers pixels) pour l'extraction.",
                    '5) Capacités approximatives: capacity_bits = width × height × channels; capacity_bytes = capacity_bits // 8.',
                    '6) Limites: altération peu visible visuellement mais sujette à compression lossy (JPEG) qui détruit LSB; PNG recommandé (lossless).'
                ]
            }
        else:
            image_method_details[m] = {'short': m, 'detailed_steps': ['Méthode image connue, détails non spécifiés.']}

    return JsonResponse({
        'text_methods': text_methods,
        'text_method_details': text_method_details,
        'image_methods': image_methods,
        'image_method_details': image_method_details
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def api_analyze_cover_text(request):
    """
    Analyse la capacité d'un texte à cacher des messages
    
    POST /api/stego/analyze/text/
    Body: {
        "text": "Texte à analyser..."
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        text = data.get('text')
        
        if not text:
            return JsonResponse({
                'error': 'text est requis'
            }, status=400)
        
        result = analyze_cover_text(text)
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_analyze_image_capacity(request):
    """
    Analyse la capacité d'une image à cacher des messages
    
    POST /api/stego/analyze/image/
    Body: {
        "image_data": "base64_encoded_image"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        image_data = data.get('image_data')
        
        if not image_data:
            return JsonResponse({
                'error': 'image_data est requis'
            }, status=400)
        
        # Décoder l'image
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return JsonResponse({
                'error': f'Erreur de décodage base64: {str(e)}'
            }, status=400)
        
        result = analyze_image_capacity(image_bytes)
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_create_sample_image(request):
    """
    Crée une image blanche simple pour les tests
    
    GET /api/stego/sample-image/
    Query params: width, height (optionnels)
    """
    width = int(request.GET.get('width', 200))
    height = int(request.GET.get('height', 200))
    
    try:
        image_bytes = create_sample_image(width, height)
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        return JsonResponse({
            'image_data': f'data:image/png;base64,{image_base64}',
            'width': width,
            'height': height
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


def get_decryption_steps(algorithm, ciphertext, key, decrypted_text):
    """
    Génère les étapes explicatives du déchiffrement
    """
    steps = []
    key_info = key.copy() if key else {}
    
    try:
        if algorithm == 'caesar':
            shift = key.get('shift', 0)
            steps.append(f"Algorithme: Déchiffrement de César avec décalage de {shift}")
            steps.append(f"Texte chiffré: {ciphertext}")
            steps.append(f"Pour chaque lettre, soustraire {shift} positions dans l'alphabet (modulo 26)")
            steps.append(f"Exemple: {ciphertext[0] if ciphertext else 'D'} → {chr((ord(ciphertext[0] if ciphertext else 'D') - ord('A') - shift) % 26 + ord('A'))}")
            steps.append(f"Résultat: {decrypted_text}")
            
        elif algorithm == 'affine':
            a = key.get('a', 1)
            b = key.get('b', 0)
            # Calcul de l'inverse modulaire de a
            a_inv = pow(a, -1, 26)
            steps.append(f"Algorithme: Déchiffrement affine avec a={a}, b={b}")
            steps.append(f"Calcul de l'inverse de a={a} modulo 26: a⁻¹={a_inv}")
            steps.append(f"Formule: D(y) = {a_inv} × (y - {b}) mod 26")
            steps.append(f"Texte chiffré: {ciphertext}")
            steps.append(f"Pour chaque lettre y, calculer {a_inv} × (y - {b}) mod 26")
            steps.append(f"Résultat: {decrypted_text}")
            
        elif algorithm == 'playfair':
            keyword = key.get('keyword', '')
            steps.append(f"Algorithme: Déchiffrement Playfair avec mot-clé '{keyword}'")
            steps.append(f"Utilisation de la même matrice 5×5 que pour le chiffrement")
            steps.append(f"Texte chiffré: {ciphertext}")
            steps.append(f"Déchiffrement par paires de lettres (règles inverses):")
            steps.append(f"  - Même ligne: décaler à gauche")
            steps.append(f"  - Même colonne: décaler vers le haut")
            steps.append(f"  - Rectangle: échanger les colonnes")
            steps.append(f"Résultat: {decrypted_text}")
            
        elif algorithm == 'hill':
            if 'matrix' in key:
                matrix = key['matrix']
                steps.append(f"Algorithme: Déchiffrement de Hill avec matrice 2×2")
                steps.append(f"Matrice de chiffrement: {matrix}")
                steps.append(f"Calcul de la matrice inverse modulo 26")
                steps.append(f"Texte chiffré groupé par paires: {ciphertext}")
                steps.append(f"Chaque paire est multipliée par la matrice inverse (modulo 26)")
                steps.append(f"Formule: P = K⁻¹ × C mod 26")
                steps.append(f"Résultat: {decrypted_text}")
        
        return {
            'encrypted_text': ciphertext,
            'decrypted_text': decrypted_text,
            'algorithm': algorithm,
            'steps': steps,
            'key_info': key_info
        }
        
    except Exception as e:
        return {
            'encrypted_text': ciphertext,
            'decrypted_text': decrypted_text,
            'algorithm': algorithm,
            'steps': [f"Déchiffrement effectué avec succès"],
            'key_info': key_info
        }


@csrf_exempt
def api_encrypt(request):
    """
    API endpoint pour chiffrer un message avec étapes détaillées
    
    POST /api/encrypt/
    {
        "plaintext": "HELLO",
        "algorithm": "caesar|affine|playfair|hill",
        "key": {...}
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        plaintext = data.get('plaintext', '')
        algorithm = data.get('algorithm', '')
        key = data.get('key', {})
        
        if not plaintext or not algorithm:
            return JsonResponse({'error': 'plaintext and algorithm are required'}, status=400)
        
        # Chiffrement
        if algorithm == 'caesar':
            shift = key.get('shift', 0)
            ciphertext = caesar_encrypt(plaintext, shift)
        elif algorithm == 'affine':
            a = key.get('a', 5)
            b = key.get('b', 8)
            ciphertext = encrypt_affine(plaintext, a, b)
        elif algorithm == 'playfair':
            keyword = key.get('keyword', 'KEYWORD')
            ciphertext = encrypt_playfair(plaintext, keyword)
        elif algorithm == 'hill':
            matrix = key.get('matrix', [[3, 3], [2, 5]])
            ciphertext = hill_encrypt(plaintext, matrix)
        else:
            return JsonResponse({'error': 'Invalid algorithm'}, status=400)
        
        # Générer les étapes
        steps_data = get_encryption_steps(algorithm, plaintext, key, ciphertext)
        
        return JsonResponse({
            'success': True,
            'plaintext': plaintext,
            'ciphertext': ciphertext,
            'algorithm': algorithm,
            'steps': steps_data['steps'],
            'key_info': steps_data['key_info']
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_decrypt(request):
    """
    API endpoint pour déchiffrer un message avec étapes détaillées
    
    POST /api/decrypt/
    {
        "ciphertext": "KHOOR",
        "algorithm": "caesar|affine|playfair|hill",
        "key": {...}
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        ciphertext = data.get('ciphertext', '')
        algorithm = data.get('algorithm', '')
        key = data.get('key', {})
        
        if not ciphertext or not algorithm:
            return JsonResponse({'error': 'ciphertext and algorithm are required'}, status=400)
        
        # Déchiffrement
        if algorithm == 'caesar':
            shift = key.get('shift', 0)
            plaintext = caesar_decrypt(ciphertext, shift)
        elif algorithm == 'affine':
            a = key.get('a', 5)
            b = key.get('b', 8)
            plaintext = decrypt_affine(ciphertext, a, b)
        elif algorithm == 'playfair':
            keyword = key.get('keyword', 'KEYWORD')
            plaintext = decrypt_playfair(ciphertext, keyword)
        elif algorithm == 'hill':
            matrix = key.get('matrix', [[3, 3], [2, 5]])
            plaintext = hill_decrypt(ciphertext, matrix)
        else:
            return JsonResponse({'error': 'Invalid algorithm'}, status=400)
        
        # Générer les étapes
        steps_data = get_decryption_steps(algorithm, ciphertext, key, plaintext)
        
        return JsonResponse({
            'success': True,
            'ciphertext': ciphertext,
            'plaintext': plaintext,
            'algorithm': algorithm,
            'steps': steps_data['steps'],
            'key_info': steps_data['key_info']
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)



@csrf_exempt
def api_captcha_generate(request):
    """
    Génère une image CAPTCHA, stocke le code dans la session et renvoie l'image en base64
    
    GET /captcha/generate/
    Optional query/body:
      - length: int (default 5)
      - width: int (default 160)
      - height: int (default 60)
      - ttl_seconds: int (default 180)
    """
    try:
        # Support GET or POST for convenience
        params = {}
        if request.method == 'POST':
            try:
                params = json.loads(request.body or '{}')
            except Exception:
                params = {}
        else:
            params = request.GET

        length = int(params.get('length', 5))
        width = int(params.get('width', 160))
        height = int(params.get('height', 60))
        ttl_seconds = int(params.get('ttl_seconds', 180))

        # Construire un code avec lettres/chiffres, éviter ambiguités excessives
        alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # sans I, O, 0, 1
        code = ''.join(random.choice(alphabet) for _ in range(max(3, min(8, length))))

        # Enregistrer en session pour vérification ultérieure
        request.session['captcha_code'] = code
        request.session['captcha_generated_at'] = time.time()
        request.session['captcha_ttl'] = ttl_seconds

        # Créer l'image
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        try:
            # Police par défaut (portable); on évite de dépendre de fichiers systèmes
            font = ImageFont.load_default()
        except Exception:
            font = None

        # Ajouter un léger bruit de fond (lignes)
        for _ in range(8):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            color = tuple(random.randint(150, 220) for _ in range(3))
            draw.line((x1, y1, x2, y2), fill=color, width=1)

        # Dessiner le code avec un léger jitter
        margin_x = 10
        spacing = max(20, (width - 2 * margin_x) // max(1, len(code)))
        base_y = height // 2 - 8
        for i, ch in enumerate(code):
            x = margin_x + i * spacing + random.randint(-2, 2)
            y = base_y + random.randint(-4, 4)
            color = tuple(random.randint(0, 120) for _ in range(3))
            draw.text((x, y), ch, font=font, fill=color)

        # Exporter en PNG base64
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return JsonResponse({
            'image_data': f'data:image/png;base64,{b64}',
            'length': len(code),
            'ttl_seconds': ttl_seconds,
            'success': True
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_captcha_verify(request):
    """
    Vérifie un code CAPTCHA contre la valeur stockée en session
    
    POST /captcha/verify/
    Body: { "captcha": "ABCDE" }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json.loads(request.body or '{}')
        user_code = str(data.get('captcha', '')).strip()

        expected = request.session.get('captcha_code')
        generated_at = float(request.session.get('captcha_generated_at', 0) or 0)
        ttl_seconds = int(request.session.get('captcha_ttl', 180))

        if not expected:
            return JsonResponse({'error': 'No CAPTCHA in session', 'captcha_required': True}, status=400)

        # Vérifier l’expiration
        if generated_at and ttl_seconds and (time.time() - generated_at) > ttl_seconds:
            # Expiré: invalider et signaler
            try:
                del request.session['captcha_code']
                del request.session['captcha_generated_at']
                del request.session['captcha_ttl']
            except Exception:
                pass
            return JsonResponse({'error': 'CAPTCHA expiré', 'captcha_required': True}, status=400)

        if user_code and expected and user_code.upper() == str(expected).upper():
            # Succès: on peut invalider pour éviter réutilisation
            try:
                del request.session['captcha_code']
                del request.session['captcha_generated_at']
                del request.session['captcha_ttl']
            except Exception:
                pass
            return JsonResponse({'success': True, 'message': 'CAPTCHA vérifié'})

        return JsonResponse({'error': 'CAPTCHA incorrect', 'captcha_required': True}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



