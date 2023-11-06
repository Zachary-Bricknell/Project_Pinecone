from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_ROLES = (
        ('GUEST', 'Guest'),
        ('AUTHORIZED', 'Authorized'),
        ('ADMIN', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='GUEST')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = 'GUEST'
        super(UserProfile, self).save(*args, **kwargs)

