from django.db import models
from django.conf import settings

class Patient(models.Model):
    RELATIONSHIP_CHOICES = [
        ("self", "Self"),
        ("child", "Child"),
        ("other", "Other dependent"),
    ]

    guardian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dependents",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20, blank=True)
    relationship = models.CharField(
        max_length=10, choices=RELATIONSHIP_CHOICES, default="self"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_relationship_display()})"

