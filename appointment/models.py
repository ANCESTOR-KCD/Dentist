from django.db import models
from patients.models import Patient

class Appointment(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="appointments"
    )
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    service = models.CharField(
        max_length=20,
        choices=[
            ("checkup", "Checkup & Clean"),
            ("filling", "Filling"),
            ("whitening", "Whitening"),
            ("root_canal", "Root Canal"),
            ("braces", "Braces"),
            ("emergency", "Emergency"),
        ],
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("cancelled", "Cancelled"),
            ("completed", "Completed"),
        ],
        default="pending",
    )

    def __str__(self):
        return f"{self.patient} — {self.get_service_display()} on {self.date} at {self.time} ({self.get_status_display()})"