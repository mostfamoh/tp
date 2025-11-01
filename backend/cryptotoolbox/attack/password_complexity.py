"""
Analyse de la complexité des mots de passe et temps d'attaque
Partie 3 : Étude de différents cas de complexité
"""

import itertools
import time
from typing import List, Dict, Any
import string


class PasswordComplexityAnalyzer:
    """Analyse la complexité et le temps d'attaque de différents types de mots de passe"""
    
    def __init__(self):
        # Vitesse d'attaque estimée (tests/seconde)
        self.attack_speed = {
            'bruteforce_local': 1_000_000,      # 1 million de tests/sec (local)
            'bruteforce_gpu': 100_000_000,      # 100 millions de tests/sec (GPU)
            'bruteforce_network': 1000,          # 1000 tests/sec (limitation réseau)
            'dictionary': 10_000                 # 10k mots/sec (dictionnaire)
        }
    
    def calculate_keyspace(self, charset_size: int, password_length: int) -> int:
        """
        Calcule l'espace de clés possible
        Formule: charset_size ^ password_length
        """
        return charset_size ** password_length
    
    def format_time(self, seconds: float) -> str:
        """Formate le temps en unités lisibles"""
        if seconds < 1:
            return f"{seconds * 1000:.2f} millisecondes"
        elif seconds < 60:
            return f"{seconds:.2f} secondes"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.2f} heures"
        elif seconds < 31536000:
            days = seconds / 86400
            return f"{days:.2f} jours"
        else:
            years = seconds / 31536000
            return f"{years:.2f} années"
    
    def analyze_case_1(self) -> Dict[str, Any]:
        """
        CAS 1: Mot de passe de 3 caractères
        Chaque caractère peut prendre les valeurs : 0, 1, 2
        Charset: {0, 1, 2} - 3 caractères possibles
        Longueur: 3
        Espace de clés: 3^3 = 27
        """
        charset = ['0', '1', '2']
        length = 3
        keyspace = self.calculate_keyspace(len(charset), length)
        
        # Temps d'attaque selon différentes méthodes
        times = {}
        for method, speed in self.attack_speed.items():
            time_seconds = keyspace / speed
            times[method] = {
                'seconds': time_seconds,
                'formatted': self.format_time(time_seconds)
            }
        
        return {
            'case': 'Cas 1: Mot de passe 3 caractères (0,1,2)',
            'charset': ''.join(charset),
            'charset_size': len(charset),
            'password_length': length,
            'keyspace': keyspace,
            'keyspace_formatted': f"{keyspace:,}",
            'times': times,
            'security_level': 'TRES FAIBLE [!!!]',
            'recommendation': 'Crackable instantanement. NE JAMAIS UTILISER.',
            'examples': ['000', '012', '222', '121']
        }
    
    def analyze_case_2(self) -> Dict[str, Any]:
        """
        CAS 2: Mot de passe de 6 caractères
        Chaque caractère peut prendre les valeurs : 0..9
        Charset: {0-9} - 10 caractères possibles
        Longueur: 6
        Espace de clés: 10^6 = 1,000,000
        """
        charset = list(string.digits)  # '0123456789'
        length = 6
        keyspace = self.calculate_keyspace(len(charset), length)
        
        times = {}
        for method, speed in self.attack_speed.items():
            time_seconds = keyspace / speed
            times[method] = {
                'seconds': time_seconds,
                'formatted': self.format_time(time_seconds)
            }
        
        return {
            'case': 'Cas 2: Mot de passe 6 caractères (0-9)',
            'charset': ''.join(charset),
            'charset_size': len(charset),
            'password_length': length,
            'keyspace': keyspace,
            'keyspace_formatted': f"{keyspace:,}",
            'times': times,
            'security_level': 'FAIBLE [!!]',
            'recommendation': 'Crackable en quelques secondes. Eviter pour des donnees sensibles.',
            'examples': ['000000', '123456', '999999', '567890']
        }
    
    def analyze_case_3(self) -> Dict[str, Any]:
        """
        CAS 3: Mot de passe de 6 caractères
        Chaque caractère peut prendre les valeurs : a-z, A-Z, 0-9, +, *, et caractères spéciaux
        Charset: {a-z, A-Z, 0-9, caractères spéciaux} - 95 caractères ASCII imprimables
        Longueur: 6
        Espace de clés: 95^6 = 735,091,890,625 (735 milliards)
        """
        # Tous les caractères ASCII imprimables
        charset = (
            string.ascii_lowercase +  # a-z (26)
            string.ascii_uppercase +  # A-Z (26)
            string.digits +            # 0-9 (10)
            string.punctuation         # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ (33)
        )  # Total: 95 caractères
        
        length = 6
        keyspace = self.calculate_keyspace(len(charset), length)
        
        times = {}
        for method, speed in self.attack_speed.items():
            time_seconds = keyspace / speed
            times[method] = {
                'seconds': time_seconds,
                'formatted': self.format_time(time_seconds)
            }
        
        return {
            'case': 'Cas 3: Mot de passe 6 caractères (a-z,A-Z,0-9,spéciaux)',
            'charset': charset,
            'charset_size': len(charset),
            'password_length': length,
            'keyspace': keyspace,
            'keyspace_formatted': f"{keyspace:,}",
            'times': times,
            'security_level': 'MOYEN [~]',
            'recommendation': 'Acceptable pour usage basique. Preferer 8+ caracteres pour donnees sensibles.',
            'examples': ['aB3$9z', 'X+7*pQ', '!mK2@v', 'Tr9#sL']
        }
    
    def run_practical_attack_case_1(self, target_password: str) -> Dict[str, Any]:
        """
        Attaque pratique sur CAS 1 (3 caractères, 0-1-2)
        """
        charset = ['0', '1', '2']
        length = 3
        
        start_time = time.time()
        attempts = 0
        found = False
        found_password = None
        
        # Générer toutes les combinaisons possibles
        for combination in itertools.product(charset, repeat=length):
            candidate = ''.join(combination)
            attempts += 1
            
            if candidate == target_password:
                found = True
                found_password = candidate
                break
        
        elapsed_time = time.time() - start_time
        
        return {
            'target': target_password,
            'found': found,
            'password': found_password,
            'attempts': attempts,
            'total_possible': 3 ** 3,
            'time_seconds': elapsed_time,
            'time_formatted': self.format_time(elapsed_time),
            'speed': attempts / elapsed_time if elapsed_time > 0 else 0
        }
    
    def run_practical_attack_case_2(self, target_password: str, max_attempts: int = None) -> Dict[str, Any]:
        """
        Attaque pratique sur CAS 2 (6 caractères, 0-9)
        """
        charset = string.digits
        length = 6
        
        start_time = time.time()
        attempts = 0
        found = False
        found_password = None
        
        total_possible = 10 ** 6
        max_attempts = max_attempts or total_possible
        
        # Générer les combinaisons
        for combination in itertools.product(charset, repeat=length):
            candidate = ''.join(combination)
            attempts += 1
            
            if candidate == target_password:
                found = True
                found_password = candidate
                break
            
            if attempts >= max_attempts:
                break
        
        elapsed_time = time.time() - start_time
        
        return {
            'target': target_password,
            'found': found,
            'password': found_password,
            'attempts': attempts,
            'total_possible': total_possible,
            'time_seconds': elapsed_time,
            'time_formatted': self.format_time(elapsed_time),
            'speed': attempts / elapsed_time if elapsed_time > 0 else 0,
            'completed': attempts >= total_possible
        }
    
    def run_practical_attack_case_3(self, target_password: str, max_attempts: int = 100000) -> Dict[str, Any]:
        """
        Attaque pratique sur CAS 3 (6 caractères, complet)
        Note: Limité à max_attempts car l'espace total est énorme (735 milliards)
        """
        charset = (
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits + 
            string.punctuation
        )
        length = 6
        
        start_time = time.time()
        attempts = 0
        found = False
        found_password = None
        
        total_possible = 95 ** 6
        
        # Générer les combinaisons (limité)
        for combination in itertools.product(charset, repeat=length):
            candidate = ''.join(combination)
            attempts += 1
            
            if candidate == target_password:
                found = True
                found_password = candidate
                break
            
            if attempts >= max_attempts:
                break
        
        elapsed_time = time.time() - start_time
        
        return {
            'target': target_password,
            'found': found,
            'password': found_password,
            'attempts': attempts,
            'max_attempts': max_attempts,
            'total_possible': total_possible,
            'time_seconds': elapsed_time,
            'time_formatted': self.format_time(elapsed_time),
            'speed': attempts / elapsed_time if elapsed_time > 0 else 0,
            'completed': False,  # Toujours partiel pour ce cas
            'percentage_tested': (attempts / total_possible) * 100
        }
    
    def get_protection_recommendations(self) -> Dict[str, Any]:
        """
        Propose des solutions de protection contre les attaques
        """
        return {
            'title': 'Protection contre les Attaques par Force Brute et Dictionnaire',
            'strategies': [
                {
                    'name': '1. Augmenter la Complexité du Mot de Passe',
                    'techniques': [
                        'Longueur minimale de 12 caractères (recommandé: 16+)',
                        'Mélange obligatoire: minuscules, majuscules, chiffres, symboles',
                        'Éviter les mots du dictionnaire et suites logiques',
                        'Utiliser des phrases de passe (passphrases) : "J\'aime#Les3Chats!"'
                    ],
                    'effectiveness': 'HAUTE [++]',
                    'impact': 'Augmente exponentiellement l\'espace de cles'
                },
                {
                    'name': '2. Limitation du Taux de Tentatives (Rate Limiting)',
                    'techniques': [
                        'Limiter à 5 tentatives par minute',
                        'Blocage temporaire après 5 échecs (5-30 minutes)',
                        'Blocage permanent après 10 échecs consécutifs',
                        'Système de CAPTCHA après 3 tentatives échouées'
                    ],
                    'effectiveness': 'TRES HAUTE [+++]',
                    'impact': 'Rend les attaques bruteforce impraticables'
                },
                {
                    'name': '3. Salage et Hachage Robuste (Salting & Hashing)',
                    'techniques': [
                        'Utiliser bcrypt, Argon2 ou PBKDF2 (pas MD5/SHA1)',
                        'Ajouter un salt unique par utilisateur',
                        'Cout de calcul eleve (work factor): ralentit les attaques',
                        'Stocker: hash(password + salt) avec salt aleatoire'
                    ],
                    'effectiveness': 'TRES HAUTE [+++]',
                    'impact': 'Meme si la base est volee, mots de passe proteges',
                    'example_python': '''
import bcrypt

# Hachage sécurisé
password = b"MonMotDePasse123!"
salt = bcrypt.gensalt(rounds=12)  # work factor = 12
hashed = bcrypt.hashpw(password, salt)

# Vérification
if bcrypt.checkpw(password, hashed):
    print("Mot de passe correct!")
'''
                },
                {
                    'name': '4. Authentification Multi-Facteurs (MFA/2FA)',
                    'techniques': [
                        'Code SMS/Email (facteur possession)',
                        'Application TOTP (Google Authenticator, Authy)',
                        'Cle de securite physique (YubiKey, FIDO2)',
                        'Biometrie (empreinte digitale, reconnaissance faciale)'
                    ],
                    'effectiveness': 'TRES HAUTE [+++]',
                    'impact': 'Meme si le mot de passe est compromis, acces refuse'
                },
                {
                    'name': '5. Detection d\'Anomalies et Monitoring',
                    'techniques': [
                        'Alertes sur tentatives multiples echouees',
                        'Detection de patterns suspects (geolocalisation, horaire)',
                        'Analyse comportementale (vitesse de frappe, souris)',
                        'Logs d\'audit complets avec timestamps'
                    ],
                    'effectiveness': 'MOYENNE-HAUTE [++]',
                    'impact': 'Permet de reagir rapidement aux attaques'
                },
                {
                    'name': '6. Chiffrement du Mot de Passe en Transit',
                    'techniques': [
                        'HTTPS/TLS obligatoire pour toute transmission',
                        'Pas de transmission en clair (HTTP interdit)',
                        'Certificate pinning pour applications mobiles',
                        'HSTS (HTTP Strict Transport Security)'
                    ],
                    'effectiveness': 'HAUTE [++]',
                    'impact': 'Protection contre les attaques man-in-the-middle'
                },
                {
                    'name': '7. Expiration et Rotation des Mots de Passe',
                    'techniques': [
                        'Changement obligatoire tous les 90 jours (donnees sensibles)',
                        'Empecher la reutilisation des 5 derniers mots de passe',
                        'Detection de mots de passe compromis (Have I Been Pwned API)',
                        'Notification proactive en cas de fuite de base de donnees'
                    ],
                    'effectiveness': 'MOYENNE [+]',
                    'impact': 'Limite la duree de validite d\'un mot de passe compromis'
                },
                {
                    'name': '8. Education des Utilisateurs',
                    'techniques': [
                        'Formation sur la creation de mots de passe robustes',
                        'Sensibilisation aux attaques de phishing',
                        'Utilisation recommandee de gestionnaires de mots de passe',
                        'Indicateur visuel de force du mot de passe lors de la creation'
                    ],
                    'effectiveness': 'MOYENNE [+]',
                    'impact': 'Reduit les erreurs humaines'
                }
            ],
            'implementation_example': {
                'django_middleware': '''
# Protection Rate Limiting dans Django
from django.core.cache import cache
from django.http import HttpResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.path == '/api/login/':
            ip = request.META.get('REMOTE_ADDR')
            key = f'login_attempts_{ip}'
            attempts = cache.get(key, 0)
            
            if attempts >= 5:
                return HttpResponse('Too many attempts. Try again in 5 minutes.', status=429)
            
            # Incrémenter et expirer après 5 minutes
            cache.set(key, attempts + 1, 300)
        
        return self.get_response(request)
''',
                'bcrypt_implementation': '''
# Utilisation de bcrypt pour le hachage sécurisé
import bcrypt
from django.contrib.auth.hashers import BasePasswordHasher

class BcryptPasswordHasher(BasePasswordHasher):
    algorithm = "bcrypt"
    
    def encode(self, password, salt):
        bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))
        return f"{self.algorithm}${bcrypt_hash.decode('utf-8')}"
    
    def verify(self, password, encoded):
        algorithm, hash_value = encoded.split('$', 1)
        return bcrypt.checkpw(password.encode('utf-8'), hash_value.encode('utf-8'))
'''
            },
            'summary': {
                'critical_measures': [
                    '[OK] Mots de passe longs et complexes (12+ caracteres)',
                    '[OK] Rate limiting strict (5 tentatives/5min)',
                    '[OK] Hachage avec bcrypt/Argon2 + salt unique',
                    '[OK] HTTPS obligatoire',
                    '[OK] MFA pour comptes sensibles'
                ],
                'defense_in_depth': 'Utiliser plusieurs couches de protection simultanement',
                'cost_benefit': 'L\'attaquant doit investir plus de ressources que la valeur des donnees'
            }
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Génère un rapport complet sur les 3 cas avec protections
        """
        return {
            'title': 'Analyse Complète de la Complexité des Mots de Passe',
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'cases': [
                self.analyze_case_1(),
                self.analyze_case_2(),
                self.analyze_case_3()
            ],
            'protections': self.get_protection_recommendations(),
            'comparison_table': self.generate_comparison_table()
        }
    
    def generate_comparison_table(self) -> Dict[str, Any]:
        """
        Génère un tableau comparatif des 3 cas
        """
        case1 = self.analyze_case_1()
        case2 = self.analyze_case_2()
        case3 = self.analyze_case_3()
        
        return {
            'headers': ['Caractéristique', 'Cas 1', 'Cas 2', 'Cas 3'],
            'rows': [
                ['Longueur', '3', '6', '6'],
                ['Charset', '0-2', '0-9', 'a-z,A-Z,0-9,spéciaux'],
                ['Taille charset', '3', '10', '95'],
                ['Espace de clés', case1['keyspace_formatted'], case2['keyspace_formatted'], case3['keyspace_formatted']],
                ['Temps (bruteforce local)', 
                 case1['times']['bruteforce_local']['formatted'],
                 case2['times']['bruteforce_local']['formatted'],
                 case3['times']['bruteforce_local']['formatted']],
                ['Temps (GPU)', 
                 case1['times']['bruteforce_gpu']['formatted'],
                 case2['times']['bruteforce_gpu']['formatted'],
                 case3['times']['bruteforce_gpu']['formatted']],
                ['Niveau de sécurité', case1['security_level'], case2['security_level'], case3['security_level']]
            ]
        }


# Fonction utilitaire pour tests rapides
def quick_analysis():
    """Analyse rapide des 3 cas"""
    analyzer = PasswordComplexityAnalyzer()
    
    print("=" * 80)
    print("ANALYSE DE COMPLEXITÉ DES MOTS DE PASSE - PARTIE 3")
    print("=" * 80)
    
    # Cas 1
    case1 = analyzer.analyze_case_1()
    print(f"\n{'=' * 80}")
    print(f"{case1['case']}")
    print(f"{'=' * 80}")
    print(f"Charset: {case1['charset']} (taille: {case1['charset_size']})")
    print(f"Longueur: {case1['password_length']}")
    print(f"Espace de clés: {case1['keyspace_formatted']}")
    print(f"Sécurité: {case1['security_level']}")
    print(f"\nTemps d'attaque:")
    for method, data in case1['times'].items():
        print(f"  - {method}: {data['formatted']}")
    
    # Cas 2
    case2 = analyzer.analyze_case_2()
    print(f"\n{'=' * 80}")
    print(f"{case2['case']}")
    print(f"{'=' * 80}")
    print(f"Charset: {case2['charset']} (taille: {case2['charset_size']})")
    print(f"Longueur: {case2['password_length']}")
    print(f"Espace de clés: {case2['keyspace_formatted']}")
    print(f"Sécurité: {case2['security_level']}")
    print(f"\nTemps d'attaque:")
    for method, data in case2['times'].items():
        print(f"  - {method}: {data['formatted']}")
    
    # Cas 3
    case3 = analyzer.analyze_case_3()
    print(f"\n{'=' * 80}")
    print(f"{case3['case']}")
    print(f"{'=' * 80}")
    print(f"Charset: [a-z,A-Z,0-9,spéciaux] (taille: {case3['charset_size']})")
    print(f"Longueur: {case3['password_length']}")
    print(f"Espace de clés: {case3['keyspace_formatted']}")
    print(f"Sécurité: {case3['security_level']}")
    print(f"\nTemps d'attaque:")
    for method, data in case3['times'].items():
        print(f"  - {method}: {data['formatted']}")
    
    print(f"\n{'=' * 80}")
    print("CONCLUSION")
    print(f"{'=' * 80}")
    print("Cas 1: DANGEREUX - Crackable instantanément")
    print("Cas 2: FAIBLE - Crackable en secondes/minutes")
    print("Cas 3: MOYEN - Nécessite plus de temps mais 8+ caractères recommandés")
    print("=" * 80)


if __name__ == "__main__":
    quick_analysis()
