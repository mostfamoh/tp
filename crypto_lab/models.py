from django.db import models

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

    def __str__(self):
        return f"{self.username}({self.algorithm})"
                                         
