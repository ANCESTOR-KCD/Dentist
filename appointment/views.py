from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from patients.models import Patient
from .models import Appointment


def _ensure_self_patient(user):
#    Every logged-in user gets a 'self' Patient profile automatically,
#     so they can book for themselves without filling out a form first.
    patient, created = Patient.objects.get_or_create(
        guardian=user,
        relationship="self",
        defaults={
            "first_name": user.first_name or user.username,
            "last_name": user.last_name,
            "email": user.email,
            "date_of_birth": "2000-01-01",  # placeholder; user can edit later
        },
    )
    return patient


@login_required
def appointment(request):
    _ensure_self_patient(request.user)
    patients = Patient.objects.filter(guardian=request.user).order_by(
        "-relationship", "first_name"
    )
    return render(request, "appointment/appointment.html", {"patients": patients})


@login_required
@require_POST
def add_dependent(request):
    """Called when the guardian adds a child/other dependent from the booking form."""
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    dob = request.POST.get("date_of_birth", "").strip()

    if not first_name or not dob:
        return JsonResponse({"ok": False, "error": "First name and date of birth are required."}, status=400)

    patient = Patient.objects.create(
        guardian=request.user,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=dob,
        relationship="child",
    )
    return JsonResponse({
        "ok": True,
        "patient": {"id": patient.id, "label": str(patient)},
    })


@login_required
@require_POST
def book_appointment(request):
    patient_id = request.POST.get("patient_id")
    service = request.POST.get("service")
    date_str = request.POST.get("date")
    time_str = request.POST.get("time")
    notes = request.POST.get("notes", "")

    if not all([patient_id, service, date_str, time_str]):
        return JsonResponse({"ok": False, "error": "Missing required fields."}, status=400)

    try:
        patient = Patient.objects.get(id=patient_id, guardian=request.user)
    except Patient.DoesNotExist:
        return JsonResponse({"ok": False, "error": "That patient doesn't belong to your account."}, status=403)

    try:
        parsed_time = datetime.strptime(time_str.strip(), "%I:%M %p").time()
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid time format."}, status=400)

    try:
        parsed_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid date format."}, status=400)

    appt = Appointment.objects.create(
        patient=patient,
        service=service,
        date=parsed_date,
        time=parsed_time,
        notes=notes,
    )
    return JsonResponse({
        "ok": True,
        "appointment": {
            "id": appt.id,
            "patient": str(appt.patient),
            "service": appt.get_service_display(),
            "date": appt.date.strftime("%B %d, %Y"),
            "time": appt.time.strftime("%I:%M %p").lstrip("0"),
        },
    })
