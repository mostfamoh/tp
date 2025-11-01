"""
Password Complexity Analysis and Attack Simulation Module

This module analyzes password strength for three complexity cases:
1. 3 characters from {0, 1, 2} - Keyspace: 3^3 = 27
2. 6 characters from {0-9} - Keyspace: 10^6 = 1,000,000
3. 6 characters from {a-z, A-Z, 0-9, special chars} - Keyspace: ~95^6 = 735,091,890,625

It simulates brute-force and dictionary attacks to measure real-world attack times.
"""

import time
import itertools
import string
import json
from typing import Dict, List, Tuple, Any


class PasswordComplexityCase:
    """Represents a password complexity case with its charset and length."""
    
    def __init__(self, name: str, charset: str, length: int, description: str):
        self.name = name
        self.charset = charset
        self.length = length
        self.description = description
        self.keyspace_size = len(charset) ** length
    
    def generate_all_passwords(self) -> List[str]:
        """Generate all possible passwords for this case (use with caution for large keyspaces)."""
        return [''.join(p) for p in itertools.product(self.charset, repeat=self.length)]
    
    def generate_sample_passwords(self, count: int) -> List[str]:
        """Generate a sample of passwords."""
        import random
        return [''.join(random.choice(self.charset) for _ in range(self.length)) for _ in range(count)]
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this password case."""
        return {
            'name': self.name,
            'description': self.description,
            'charset': self.charset,
            'charset_size': len(self.charset),
            'password_length': self.length,
            'keyspace_size': self.keyspace_size,
            'keyspace_formatted': f"{self.keyspace_size:,}"
        }


class PasswordAttackSimulator:
    """Simulates brute-force and dictionary attacks on passwords."""
    
    def __init__(self):
        self.cases = {
            'case1': PasswordComplexityCase(
                name="Cas 1: Très Faible",
                charset="012",
                length=3,
                description="3 caractères parmi {0, 1, 2}"
            ),
            'case2': PasswordComplexityCase(
                name="Cas 2: Faible",
                charset="0123456789",
                length=6,
                description="6 caractères numériques (0-9)"
            ),
            'case3': PasswordComplexityCase(
                name="Cas 3: Moyen",
                charset=string.ascii_letters + string.digits + string.punctuation,
                length=6,
                description="6 caractères alphanumériques + caractères spéciaux"
            )
        }
    
    def brute_force_attack(self, target_password: str, case: PasswordComplexityCase, 
                          max_attempts: int = None) -> Dict[str, Any]:
        """
        Simulate a brute-force attack.
        
        Args:
            target_password: The password to crack
            case: The password complexity case
            max_attempts: Maximum number of attempts (None = unlimited)
        
        Returns:
            Dictionary with attack results
        """
        start_time = time.perf_counter()
        attempts = 0
        found = False
        found_password = None
        
        # For very large keyspaces, we limit the attack
        if case.keyspace_size > 10_000_000 and max_attempts is None:
            max_attempts = 100_000  # Safety limit
        
        for candidate in itertools.product(case.charset, repeat=case.length):
            attempts += 1
            candidate_str = ''.join(candidate)
            
            if candidate_str == target_password:
                found = True
                found_password = candidate_str
                break
            
            if max_attempts and attempts >= max_attempts:
                break
        
        elapsed_time = time.perf_counter() - start_time
        
        return {
            'attack_type': 'brute_force',
            'success': found,
            'target_password': target_password if found else None,
            'found_password': found_password,
            'attempts': attempts,
            'time_seconds': round(elapsed_time, 6),
            'attempts_per_second': round(attempts / elapsed_time if elapsed_time > 0 else 0, 2),
            'keyspace_size': case.keyspace_size,
            'percentage_searched': round((attempts / case.keyspace_size) * 100, 4) if case.keyspace_size > 0 else 0
        }
    
    def dictionary_attack(self, target_password: str, dictionary: List[str]) -> Dict[str, Any]:
        """
        Simulate a dictionary attack.
        
        Args:
            target_password: The password to crack
            dictionary: List of password candidates
        
        Returns:
            Dictionary with attack results
        """
        start_time = time.perf_counter()
        attempts = 0
        found = False
        found_password = None
        
        for candidate in dictionary:
            attempts += 1
            if candidate == target_password:
                found = True
                found_password = candidate
                break
        
        elapsed_time = time.perf_counter() - start_time
        
        return {
            'attack_type': 'dictionary',
            'success': found,
            'target_password': target_password if found else None,
            'found_password': found_password,
            'attempts': attempts,
            'time_seconds': round(elapsed_time, 6),
            'attempts_per_second': round(attempts / elapsed_time if elapsed_time > 0 else 0, 2),
            'dictionary_size': len(dictionary)
        }
    
    def run_comprehensive_analysis(self, case_id: str, sample_password: str = None) -> Dict[str, Any]:
        """
        Run a comprehensive analysis including both attack types.
        
        Args:
            case_id: ID of the password case ('case1', 'case2', 'case3')
            sample_password: Optional specific password to test (random if None)
        
        Returns:
            Complete analysis results
        """
        if case_id not in self.cases:
            return {'error': f'Invalid case_id: {case_id}'}
        
        case = self.cases[case_id]
        
        # Generate or use provided password
        if sample_password is None:
            sample_password = case.generate_sample_passwords(1)[0]
        
        # Validate password matches case requirements
        if len(sample_password) != case.length:
            return {'error': f'Password length must be {case.length}'}
        if not all(c in case.charset for c in sample_password):
            return {'error': f'Password contains invalid characters for this case'}
        
        results = {
            'case_info': case.get_info(),
            'test_password': sample_password,
            'attacks': {}
        }
        
        # Brute-force attack
        if case.keyspace_size <= 1_000_000:  # Only for feasible keyspaces
            bf_result = self.brute_force_attack(sample_password, case)
            results['attacks']['brute_force'] = bf_result
            
            # Estimate time for full keyspace if not fully searched
            if bf_result['percentage_searched'] < 100:
                avg_time_per_attempt = bf_result['time_seconds'] / bf_result['attempts']
                estimated_full_time = avg_time_per_attempt * case.keyspace_size
                results['attacks']['brute_force']['estimated_full_keyspace_time'] = {
                    'seconds': round(estimated_full_time, 2),
                    'minutes': round(estimated_full_time / 60, 2),
                    'hours': round(estimated_full_time / 3600, 2),
                    'days': round(estimated_full_time / 86400, 2)
                }
        else:
            # For large keyspaces, run limited brute-force and extrapolate
            bf_result = self.brute_force_attack(sample_password, case, max_attempts=100_000)
            results['attacks']['brute_force'] = bf_result
            results['attacks']['brute_force']['note'] = 'Limited to 100,000 attempts due to large keyspace'
            
            # Extrapolate to full keyspace
            if bf_result['attempts'] > 0:
                avg_time_per_attempt = bf_result['time_seconds'] / bf_result['attempts']
                estimated_full_time = avg_time_per_attempt * case.keyspace_size
                results['attacks']['brute_force']['estimated_full_keyspace_time'] = {
                    'seconds': round(estimated_full_time, 2),
                    'minutes': round(estimated_full_time / 60, 2),
                    'hours': round(estimated_full_time / 3600, 2),
                    'days': round(estimated_full_time / 86400, 2),
                    'years': round(estimated_full_time / (86400 * 365.25), 2)
                }
        
        # Dictionary attack (generate a sample dictionary)
        dictionary_size = min(10000, case.keyspace_size)
        dictionary = case.generate_sample_passwords(dictionary_size)
        
        # Ensure target password is in dictionary for a fair test
        if sample_password not in dictionary:
            # Insert at random position
            import random
            insert_pos = random.randint(0, len(dictionary))
            dictionary.insert(insert_pos, sample_password)
        
        dict_result = self.dictionary_attack(sample_password, dictionary)
        results['attacks']['dictionary'] = dict_result
        
        return results
    
    def get_protection_recommendations(self) -> Dict[str, Any]:
        """
        Provide recommendations for password protection against attacks.
        
        Returns:
            Dictionary with security recommendations
        """
        return {
            'title': 'Recommandations pour la Protection des Mots de Passe',
            'categories': [
                {
                    'category': '1. Hachage Cryptographique Fort',
                    'recommendations': [
                        {
                            'recommendation': 'Utiliser Argon2id (recommandé)',
                            'description': 'Algorithme moderne résistant aux attaques GPU/ASIC',
                            'implementation': 'Argon2id avec paramètres: memory=64MB, iterations=3, parallelism=4'
                        },
                        {
                            'recommendation': 'Alternative: bcrypt',
                            'description': 'Algorithme éprouvé avec facteur de coût ajustable',
                            'implementation': 'bcrypt avec cost factor >= 12'
                        },
                        {
                            'recommendation': 'Alternative: scrypt',
                            'description': 'Résistant aux attaques par matériel spécialisé',
                            'implementation': 'scrypt avec N=2^14, r=8, p=1'
                        }
                    ]
                },
                {
                    'category': '2. Salage (Salt)',
                    'recommendations': [
                        {
                            'recommendation': 'Salt unique par utilisateur',
                            'description': 'Empêche les attaques par rainbow tables',
                            'implementation': 'Générer un salt aléatoire de 128 bits minimum pour chaque mot de passe'
                        },
                        {
                            'recommendation': 'Salt cryptographiquement sécurisé',
                            'description': 'Utiliser un générateur de nombres aléatoires cryptographiquement sûr',
                            'implementation': 'os.urandom() ou secrets.token_bytes() en Python'
                        }
                    ]
                },
                {
                    'category': '3. Politique de Complexité',
                    'recommendations': [
                        {
                            'recommendation': 'Longueur minimale: 12 caractères',
                            'description': 'Augmente exponentiellement la difficulté des attaques',
                            'impact': 'Keyspace pour 12 chars alphanumériques: 62^12 ≈ 3.2 × 10^21'
                        },
                        {
                            'recommendation': 'Mélange de types de caractères',
                            'description': 'Majuscules, minuscules, chiffres, caractères spéciaux',
                            'impact': 'Augmente la taille du charset de 26 à 95+'
                        },
                        {
                            'recommendation': 'Interdire les mots de passe courants',
                            'description': 'Bloquer les mots de passe dans les listes de compromission',
                            'implementation': 'Vérifier contre haveibeenpwned.com API ou liste locale'
                        }
                    ]
                },
                {
                    'category': '4. Protection contre les Attaques',
                    'recommendations': [
                        {
                            'recommendation': 'Rate Limiting',
                            'description': 'Limiter le nombre de tentatives de connexion',
                            'implementation': '5 tentatives max par 15 minutes par IP/compte'
                        },
                        {
                            'recommendation': 'Verrouillage de compte temporaire',
                            'description': 'Bloquer le compte après X tentatives échouées',
                            'implementation': 'Verrouillage de 30 minutes après 5 échecs'
                        },
                        {
                            'recommendation': 'CAPTCHA après échecs',
                            'description': 'Ralentir les attaques automatisées',
                            'implementation': 'Activer CAPTCHA après 3 tentatives échouées'
                        },
                        {
                            'recommendation': 'Authentification Multi-Facteurs (MFA)',
                            'description': 'Ajouter une couche de sécurité supplémentaire',
                            'implementation': 'TOTP (Google Authenticator), SMS, ou clés de sécurité'
                        }
                    ]
                },
                {
                    'category': '5. Monitoring et Alertes',
                    'recommendations': [
                        {
                            'recommendation': 'Journalisation des tentatives',
                            'description': 'Enregistrer toutes les tentatives de connexion',
                            'implementation': 'Log timestamp, IP, username, succès/échec'
                        },
                        {
                            'recommendation': 'Alertes sur activité suspecte',
                            'description': 'Notifier l\'utilisateur et les admins',
                            'implementation': 'Email/SMS lors de tentatives multiples ou connexion inhabituelle'
                        }
                    ]
                }
            ],
            'comparison': {
                'title': 'Comparaison des Temps de Craquage',
                'note': 'Estimations basées sur 100 milliards de tentatives/seconde (GPU moderne)',
                'examples': [
                    {
                        'password': '012 (Cas 1)',
                        'keyspace': 27,
                        'time_cracked': '< 1 microseconde',
                        'security': 'TRÈS DANGEREUX'
                    },
                    {
                        'password': '123456 (Cas 2)',
                        'keyspace': 1_000_000,
                        'time_cracked': '< 1 milliseconde',
                        'security': 'TRÈS DANGEREUX'
                    },
                    {
                        'password': 'aB3!xY (Cas 3)',
                        'keyspace': 735_091_890_625,
                        'time_cracked': '~2 heures',
                        'security': 'FAIBLE'
                    },
                    {
                        'password': 'aB3!xY9$Qm (10 chars)',
                        'keyspace': '~6 × 10^19',
                        'time_cracked': '~19 ans',
                        'security': 'MOYEN'
                    },
                    {
                        'password': 'aB3!xY9$Qm7& (12 chars)',
                        'keyspace': '~5 × 10^23',
                        'time_cracked': '~160,000 ans',
                        'security': 'FORT'
                    },
                    {
                        'password': 'Mot de passe avec Argon2id',
                        'note': 'Avec hachage fort, même "123456" nécessite',
                        'time_per_attempt': '~0.5 seconde par tentative',
                        'time_cracked': '~5 millions de secondes = 58 jours',
                        'security': 'ACCEPTABLE avec rate limiting'
                    }
                ]
            }
        }


# Global instance
simulator = PasswordAttackSimulator()


def analyze_password_case(case_id: str, sample_password: str = None) -> Dict[str, Any]:
    """
    Main function to analyze a password case.
    
    Args:
        case_id: 'case1', 'case2', or 'case3'
        sample_password: Optional password to test
    
    Returns:
        Complete analysis results
    """
    return simulator.run_comprehensive_analysis(case_id, sample_password)


def get_all_cases_info() -> Dict[str, Any]:
    """Get information about all password complexity cases."""
    return {
        case_id: case.get_info() 
        for case_id, case in simulator.cases.items()
    }


def get_protection_recommendations() -> Dict[str, Any]:
    """Get password protection recommendations."""
    return simulator.get_protection_recommendations()
