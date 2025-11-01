from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class CustomUser(models.Model):
    username = models.CharField(max_length=100,unique=True)
    password_encypted = models.CharField()
    algorithm = models.CharField(max_length=20,choices=[
        ('caesar','Caesar'),
        ('affine','Affine'),
        ('playfair','playfair'),
        ('hill','hill')
    ])
    ''' FOR THE KEY'''
    key_data = models.JSONField() 
    
    # Protection contre les tentatives de connexion
    protection_enabled = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    last_failed_attempt = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username}({self.algorithm})"
    
    def is_account_locked(self):
        """Vérifie si le compte est actuellement verrouillé"""
        if not self.protection_enabled:
            return False
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        return False
    
    def record_failed_attempt(self):
        """Enregistre une tentative de connexion échouée"""
        if not self.protection_enabled:
            return
        
        self.failed_login_attempts += 1
        self.last_failed_attempt = timezone.now()
        
        # Bloquer le compte après 3 tentatives
        if self.failed_login_attempts >= 3:
            self.account_locked_until = timezone.now() + timedelta(minutes=30)
        
        self.save()
    
    def reset_failed_attempts(self):
        """Réinitialise les tentatives échouées après une connexion réussie"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_failed_attempt = None
        self.save()
    
    def get_lock_remaining_time(self):
        """Retourne le temps restant de verrouillage en minutes"""
        if not self.is_account_locked():
            return 0
        remaining = (self.account_locked_until - timezone.now()).total_seconds() / 60
        return max(0, int(remaining))
                                         
