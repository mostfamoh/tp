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
    
    # Account protection endpoints
    path('users/<str:username>/toggle-protection/', views.api_toggle_protection, name='api_toggle_protection'),
    path('users/<str:username>/protection-status/', views.api_get_protection_status, name='api_get_protection_status'),
    path('users/<str:username>/unlock/', views.api_unlock_account, name='api_unlock_account'),
    
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
    
    # Steganography endpoints
    path('stego/text/hide/', views.api_text_stego_hide, name='api_text_stego_hide'),
    path('stego/text/extract/', views.api_text_stego_extract, name='api_text_stego_extract'),
    path('stego/image/hide/', views.api_image_stego_hide, name='api_image_stego_hide'),
    path('stego/image/extract/', views.api_image_stego_extract, name='api_image_stego_extract'),
    path('stego/methods/', views.api_stego_methods, name='api_stego_methods'),
    path('stego/analyze/text/', views.api_analyze_cover_text, name='api_analyze_cover_text'),
    path('stego/analyze/image/', views.api_analyze_image_capacity, name='api_analyze_image_capacity'),
    path('stego/sample-image/', views.api_create_sample_image, name='api_create_sample_image'),
    
    # Messaging with encryption steps endpoints
    path('api/encrypt/', views.api_encrypt, name='api_encrypt'),
    path('api/decrypt/', views.api_decrypt, name='api_decrypt'),
]

