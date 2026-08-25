from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),

    # OTP-based password reset flow
    path("reset-code/", views.request_reset_code, name="request_reset_code"),
    path("reset-code/verify/", views.verify_reset_code, name="enter_reset_code"),
    path("reset-code/new-password/", views.set_new_password, name="set_new_password"),
]