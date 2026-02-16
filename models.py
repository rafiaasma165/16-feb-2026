from django.db import models
from django.contrib.auth.models import User
from claims.models import Organization, Region

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('org_admin', 'Organization Admin'),
        ('region_manager', 'Region Manager'),
        ('practice_user', 'Practice User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='practice_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.user.username} Profile ({self.role})"