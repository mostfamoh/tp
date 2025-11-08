"""
URLs pour l'API d'attaques - TP SSAD USTHB
"""
from django.urls import path
from . import views_attacks

urlpatterns = [
    # Attaques
    path('attack/bruteforce/', views_attacks.bruteforce_attack, name='api_bruteforce'),
    path('attack/dictionary/', views_attacks.dictionary_attack, name='api_dictionary'),
    path('attack/combined/', views_attacks.combined_attack, name='api_combined'),
    path('attack/statistics/', views_attacks.get_attack_statistics, name='api_statistics'),
    path('attack/plain_bruteforce/', views_attacks.plain_bruteforce, name='api_plain_bruteforce'),
]
