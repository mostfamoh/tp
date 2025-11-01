from django.urls import path
from . import views

urlpatterns = [
    # Frontend interface
    path('', views.index, name='index'),
    
    # API endpoints
    path('regester/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    # new API endpoints for the attack runner and user inspection
    path('user/<str:username>/', views.api_get_user, name='api_get_user'),
    path('attack/full_bruteforce/', views.api_attack_full_bruteforce, name='api_attack_full_bruteforce'),
    path('attack/full_dictionary/', views.api_attack_full_dictionary, name='api_attack_full_dictionary'),
    
    # Password complexity analysis endpoints
    path('analysis/complexity/', views.api_password_complexity_analysis, name='api_password_complexity_analysis'),
    path('analysis/practical-attack/', views.api_practical_attack, name='api_practical_attack'),
    path('analysis/protection-recommendations/', views.api_protection_recommendations, name='api_protection_recommendations'),
    
    # All combinations with encryption steps
    path('analysis/all-combinations/', views.generate_all_combinations_with_encryption, name='api_all_combinations'),
    
    # New password analysis endpoints (Partie 3)
    path('password-analysis/', views.api_password_analysis, name='api_password_analysis'),
    path('password-cases-info/', views.api_password_cases_info, name='api_password_cases_info'),
    path('password-protection/', views.api_password_protection_recommendations, name='api_password_protection'),
]
