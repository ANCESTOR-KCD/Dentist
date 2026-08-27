from django.shortcuts import render

def appointment(request):
    return render(request, 'appointment/appointment.html')

