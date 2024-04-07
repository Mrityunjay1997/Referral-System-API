from .constants import *
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


"""
User role 
"""
USER_ROLE = ((1, "Admin"),(2, "Customer"))
ADMIN = 1
CUSTOMER = 2

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField("email address", null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    referral_code = models.CharField(max_length=15, null=True, blank=True)
    is_referred = models.BooleanField(default=False)
    referred_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'user'
    def __str__(self):
        return str(self.username)
