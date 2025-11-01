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
import base64


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
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


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
        
        result = hide_text_in_image(image_bytes, secret_message, method)
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
        
        result = extract_text_from_image(image_bytes, method)
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
    return JsonResponse({
        'text_methods': get_available_methods(),
        'image_methods': get_image_methods()
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



