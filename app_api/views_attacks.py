"""
Vues d'attaques - TP SSAD USTHB
Implémente les attaques par force brute et dictionnaire
avec génération de résultats JSON pour le rapport
"""
import json
import time
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from crypto_lab.models import CustomUser
from backend.cryptotoolbox.attack.attack_runner import run_attack
from math import gcd


def save_attack_result(result: dict, algorithm: str):
    """
    Sauvegarde les résultats d'une attaque dans docs/results/
    
    Args:
        result (dict): Résultats de l'attaque
        algorithm (str): Nom de l'algorithme
    """
    # Créer le dossier si nécessaire
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'docs', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Nom du fichier
    filename = f"results_{algorithm}.json"
    filepath = os.path.join(results_dir, filename)
    
    # Charger les résultats existants s'ils existent
    existing_results = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_results = json.load(f)
                if not isinstance(existing_results, list):
                    existing_results = [existing_results]
        except:
            existing_results = []
    
    # Ajouter le nouveau résultat
    existing_results.append(result)
    
    # Sauvegarder
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)


@csrf_exempt
def bruteforce_attack(request):
    """
    POST /api/attack/bruteforce/
    
    Lance une attaque par force brute et sauvegarde les résultats.
    
    Payload JSON:
    {
        "target_username": "test_alice",
        "algorithm": "caesar",  // optionnel, auto-détecté depuis la DB
        "limit": 1000,
        "max_seconds": 10,
        "playfair_keyspace": []  // requis pour Playfair
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST seulement'}, status=405)
    
    try:
        payload = json.loads(request.body)
    except:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    
    # Forcer le mode brute force
    payload['mode'] = 'bruteforce'
    
    # Exécuter l'attaque
    result = run_attack(payload)
    
    # Si succès, préparer le résultat pour sauvegarde
    if 'error' not in result and result.get('matches_count', 0) > 0:
        # Extraire le meilleur match
        best_match = result['matches'][0] if result['matches'] else None
        
        formatted_result = {
            "algorithm": result.get('algorithm'),
            "user": result.get('target_username'),
            "attack": "bruteforce",
            "attempts": result.get('attempts'),
            "time_sec": result.get('time_sec'),
            "found_password": best_match['candidate_plaintext'] if best_match else None,
            "key": best_match['candidate_key'] if best_match else None,
            "confidence": best_match['confidence'] if best_match else "none",
            "all_matches": result['matches'][:5],  # Garder les 5 premiers
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Sauvegarder
        save_attack_result(formatted_result, result.get('algorithm', 'unknown'))
    
    return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def dictionary_attack(request):
    """
    POST /api/attack/dictionary/
    
    Lance une attaque par dictionnaire et sauvegarde les résultats.
    
    Payload JSON:
    {
        "target_username": "test_alice",
        "algorithm": "caesar",  // optionnel
        "dictionary": ["PASSWORD", "SECRET", "HELLO"],
        "limit": 0,
        "max_seconds": 30
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST seulement'}, status=405)
    
    try:
        payload = json.loads(request.body)
    except:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    
    # Charger le dictionnaire depuis le fichier si non fourni
    if 'dictionary' not in payload or not payload['dictionary']:
        wordlist_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wordlist.txt')
        if os.path.exists(wordlist_path):
            with open(wordlist_path, 'r', encoding='utf-8') as f:
                payload['dictionary'] = [line.strip() for line in f if line.strip()]
        else:
            return JsonResponse({'error': 'Aucun dictionnaire fourni et wordlist.txt introuvable'}, status=400)
    
    # Forcer le mode dictionnaire
    payload['mode'] = 'dictionary'
    
    # Exécuter l'attaque
    result = run_attack(payload)
    
    # Si succès, sauvegarder
    if 'error' not in result and result.get('matches_count', 0) > 0:
        best_match = result['matches'][0] if result['matches'] else None
        
        formatted_result = {
            "algorithm": result.get('algorithm'),
            "user": result.get('target_username'),
            "attack": "dictionary",
            "attempts": result.get('attempts'),
            "time_sec": result.get('time_sec'),
            "found_password": best_match['candidate_plaintext'] if best_match else None,
            "key": best_match['candidate_key'] if best_match else None,
            "confidence": best_match['confidence'] if best_match else "none",
            "dictionary_size": len(payload.get('dictionary', [])),
            "all_matches": result['matches'][:5],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_attack_result(formatted_result, result.get('algorithm', 'unknown'))
    
    return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def combined_attack(request):
    """
    POST /api/attack/combined/
    
    Lance les deux types d'attaques (force brute + dictionnaire) et compare.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST seulement'}, status=405)
    
    try:
        payload = json.loads(request.body)
    except:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    
    username = payload.get('target_username')
    if not username:
        return JsonResponse({'error': 'target_username requis'}, status=400)
    
    # Charger le dictionnaire
    wordlist_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wordlist.txt')
    dictionary = []
    if os.path.exists(wordlist_path):
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            dictionary = [line.strip() for line in f if line.strip()]
    
    # Attaque par dictionnaire d'abord (plus rapide)
    dict_payload = payload.copy()
    dict_payload['mode'] = 'dictionary'
    dict_payload['dictionary'] = dictionary
    dict_payload['max_seconds'] = payload.get('max_seconds_dict', 10)
    
    dict_result = run_attack(dict_payload)
    
    # Si trouvé par dictionnaire, pas besoin de force brute
    if dict_result.get('matches_count', 0) > 0:
        return JsonResponse({
            "method": "dictionary",
            "success": True,
            "result": dict_result,
            "message": "Mot de passe trouvé par attaque dictionnaire"
        }, json_dumps_params={'ensure_ascii': False})
    
    # Sinon, tenter force brute
    bf_payload = payload.copy()
    bf_payload['mode'] = 'bruteforce'
    bf_payload['max_seconds'] = payload.get('max_seconds_bf', 30)
    bf_payload['limit'] = payload.get('limit', 10000)
    
    bf_result = run_attack(bf_payload)
    
    return JsonResponse({
        "method": "combined",
        "dictionary_result": dict_result,
        "bruteforce_result": bf_result,
        "success": bf_result.get('matches_count', 0) > 0
    }, json_dumps_params={'ensure_ascii': False})


def get_attack_statistics(request):
    """
    GET /api/attack/statistics/
    
    Retourne les statistiques de toutes les attaques effectuées.
    """
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'docs', 'results')
    
    if not os.path.exists(results_dir):
        return JsonResponse({
            "message": "Aucune attaque effectuée encore",
            "statistics": {}
        })
    
    stats = {
        "total_attacks": 0,
        "by_algorithm": {},
        "by_attack_type": {"bruteforce": 0, "dictionary": 0},
        "average_time": 0,
        "success_rate": 0,
        "recent_attacks": []
    }
    
    total_time = 0
    successful = 0
    
    for filename in os.listdir(results_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(results_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                    if not isinstance(results, list):
                        results = [results]
                    
                    for result in results:
                        stats["total_attacks"] += 1
                        
                        algo = result.get('algorithm', 'unknown')
                        if algo not in stats["by_algorithm"]:
                            stats["by_algorithm"][algo] = 0
                        stats["by_algorithm"][algo] += 1
                        
                        attack_type = result.get('attack', 'unknown')
                        if attack_type in stats["by_attack_type"]:
                            stats["by_attack_type"][attack_type] += 1
                        
                        if result.get('found_password'):
                            successful += 1
                        
                        total_time += result.get('time_sec', 0)
                        
                        # Garder les 10 plus récentes
                        if len(stats["recent_attacks"]) < 10:
                            stats["recent_attacks"].append({
                                "algorithm": algo,
                                "attack": attack_type,
                                "user": result.get('user'),
                                "success": bool(result.get('found_password')),
                                "time": result.get('time_sec'),
                                "timestamp": result.get('timestamp')
                            })
            except:
                pass
    
    if stats["total_attacks"] > 0:
        stats["average_time"] = round(total_time / stats["total_attacks"], 4)
        stats["success_rate"] = round((successful / stats["total_attacks"]) * 100, 2)
    
    # Trier par timestamp (plus récent en premier)
    stats["recent_attacks"] = sorted(
        stats["recent_attacks"],
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    return JsonResponse(stats, json_dumps_params={'ensure_ascii': False})
