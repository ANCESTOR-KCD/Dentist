from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 600  # 10 min expiry

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))