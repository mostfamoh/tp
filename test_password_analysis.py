"""
Script de test pour l'analyse de complexité de mots de passe (Partie 3)

Ce script teste les trois cas de complexité de mots de passe et génère
des rapports détaillés sur:
1. Les attaques par force brute
2. Les attaques par dictionnaire
3. Les recommandations de protection

Cas testés:
- Cas 1: 3 caractères parmi {0, 1, 2} - Keyspace: 27
- Cas 2: 6 caractères numériques {0-9} - Keyspace: 1,000,000
- Cas 3: 6 caractères alphanumériques + spéciaux - Keyspace: ~735 milliards
"""

import sys
import os
import json
import time

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import directly from the module to avoid __init__.py issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "password_analysis", 
    os.path.join(project_root, "backend", "cryptotoolbox", "attack", "password_analysis.py")
)
password_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(password_analysis)

analyze_password_case = password_analysis.analyze_password_case
get_all_cases_info = password_analysis.get_all_cases_info
get_protection_recommendations = password_analysis.get_protection_recommendations


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_subheader(text):
    """Print a formatted subheader."""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)


def format_time(seconds):
    """Format time in human-readable format."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.2f} microsecondes"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} millisecondes"
    elif seconds < 60:
        return f"{seconds:.2f} secondes"
    elif seconds < 3600:
        return f"{seconds / 60:.2f} minutes"
    elif seconds < 86400:
        return f"{seconds / 3600:.2f} heures"
    else:
        return f"{seconds / 86400:.2f} jours"


def test_password_case(case_id, sample_password=None):
    """Test a specific password case."""
    print_subheader(f"Test du {case_id.upper()}")
    
    result = analyze_password_case(case_id, sample_password)
    
    if 'error' in result:
        print(f"❌ Erreur: {result['error']}")
        return result
    
    # Case information
    case_info = result['case_info']
    print(f"📊 {case_info['name']}")
    print(f"   Description: {case_info['description']}")
    print(f"   Charset: {case_info['charset']}")
    print(f"   Taille du charset: {case_info['charset_size']}")
    print(f"   Longueur du mot de passe: {case_info['password_length']}")
    print(f"   Espace de clés total: {case_info['keyspace_formatted']}")
    
    # Test password
    print(f"\n🔐 Mot de passe testé: '{result['test_password']}'")
    
    # Brute-force attack results
    if 'brute_force' in result['attacks']:
        bf = result['attacks']['brute_force']
        print(f"\n⚔️  Attaque par Force Brute:")
        print(f"   Statut: {'✅ SUCCÈS' if bf['success'] else '❌ ÉCHEC'}")
        print(f"   Tentatives: {bf['attempts']:,}")
        print(f"   Temps écoulé: {format_time(bf['time_seconds'])}")
        print(f"   Vitesse: {bf['attempts_per_second']:,.0f} tentatives/seconde")
        print(f"   Espace exploré: {bf['percentage_searched']:.4f}%")
        
        if 'estimated_full_keyspace_time' in bf:
            est = bf['estimated_full_keyspace_time']
            print(f"\n   ⏱️  Temps estimé pour explorer tout l'espace:")
            if 'years' in est:
                print(f"      • {est['years']:,.2f} années")
            elif 'days' in est:
                print(f"      • {est['days']:,.2f} jours")
            elif 'hours' in est:
                print(f"      • {est['hours']:,.2f} heures")
            elif 'minutes' in est:
                print(f"      • {est['minutes']:,.2f} minutes")
            else:
                print(f"      • {est['seconds']:,.2f} secondes")
        
        if 'note' in bf:
            print(f"   ℹ️  Note: {bf['note']}")
    
    # Dictionary attack results
    if 'dictionary' in result['attacks']:
        da = result['attacks']['dictionary']
        print(f"\n📖 Attaque par Dictionnaire:")
        print(f"   Statut: {'✅ SUCCÈS' if da['success'] else '❌ ÉCHEC'}")
        print(f"   Taille du dictionnaire: {da['dictionary_size']:,}")
        print(f"   Tentatives: {da['attempts']:,}")
        print(f"   Temps écoulé: {format_time(da['time_seconds'])}")
        print(f"   Vitesse: {da['attempts_per_second']:,.0f} tentatives/seconde")
    
    return result


def main():
    """Main test function."""
    print_header("TEST DE COMPLEXITÉ DES MOTS DE PASSE - PARTIE 3")
    
    print("Ce script teste trois niveaux de complexité de mots de passe:")
    print("1. Cas 1: 3 caractères parmi {0, 1, 2}")
    print("2. Cas 2: 6 caractères numériques (0-9)")
    print("3. Cas 3: 6 caractères alphanumériques + caractères spéciaux")
    
    # Get all cases info
    print_subheader("Informations sur les Cas de Test")
    cases_info = get_all_cases_info()
    for case_id, info in cases_info.items():
        print(f"\n{case_id.upper()}:")
        print(f"  Nom: {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  Espace de clés: {info['keyspace_formatted']}")
    
    # Test each case
    all_results = {}
    
    # Case 1: Very weak (3 chars from {0,1,2})
    result1 = test_password_case('case1', '012')
    all_results['case1'] = result1
    
    # Case 2: Weak (6 numeric chars)
    result2 = test_password_case('case2', '123456')
    all_results['case2'] = result2
    
    # Case 3: Medium (6 alphanumeric + special chars)
    result3 = test_password_case('case3', 'aB3!xY')
    all_results['case3'] = result3
    
    # Protection recommendations
    print_header("RECOMMANDATIONS DE PROTECTION")
    recommendations = get_protection_recommendations()
    
    print(f"📋 {recommendations['title']}\n")
    
    for category in recommendations['categories']:
        print(f"\n🔹 {category['category']}")
        for rec in category['recommendations']:
            print(f"\n   ✓ {rec['recommendation']}")
            print(f"     {rec['description']}")
            if 'implementation' in rec:
                print(f"     💡 Implémentation: {rec['implementation']}")
            if 'impact' in rec:
                print(f"     💥 Impact: {rec['impact']}")
    
    # Comparison table
    print_header("COMPARAISON DES TEMPS DE CRAQUAGE")
    print(recommendations['comparison']['note'])
    print()
    
    for example in recommendations['comparison']['examples']:
        print(f"\n🔐 {example['password']}")
        if 'keyspace' in example:
            keyspace = example['keyspace']
            if isinstance(keyspace, (int, float)):
                print(f"   Espace: {keyspace:,}")
            else:
                print(f"   Espace: {keyspace}")
        if 'time_cracked' in example:
            print(f"   Temps: {example['time_cracked']}")
        if 'time_per_attempt' in example:
            print(f"   Temps/tentative: {example['time_per_attempt']}")
        if 'note' in example:
            print(f"   Note: {example['note']}")
        print(f"   Sécurité: {example['security']}")
    
    # Save results to file
    output_file = os.path.join(project_root, 'password_analysis_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'cases_info': cases_info,
            'test_results': all_results,
            'recommendations': recommendations
        }, f, ensure_ascii=False, indent=4)
    
    print_header("RÉSULTATS SAUVEGARDÉS")
    print(f"✅ Rapport complet sauvegardé dans: {output_file}")
    
    # Summary
    print_header("RÉSUMÉ")
    print("✅ Test du Cas 1 (3 chars, {0,1,2}): TERMINÉ")
    print("✅ Test du Cas 2 (6 chars numériques): TERMINÉ")
    print("✅ Test du Cas 3 (6 chars alphanumériques + spéciaux): TERMINÉ")
    print("✅ Recommandations de protection: GÉNÉRÉES")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
