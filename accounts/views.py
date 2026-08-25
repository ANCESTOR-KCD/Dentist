from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib import messages
from .forms import RegisterForm
from .models import PasswordResetCode


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def request_reset_code(request):
    """Step 1: user enters their email, we generate + email a code."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        user = User.objects.filter(email=email).first()

        if user:
            code = PasswordResetCode.generate_code()
            PasswordResetCode.objects.create(user=user, code=code)
            send_mail(
                subject="Your Maria Land Password Reset Code",
                message=f"Your password reset code is: {code}\n\nThis code expires in 10 minutes.",
                from_email="Maria Land<dubemchude@gmail.com>",
                recipient_list=[email],
                fail_silently=False,
            )

        messages.info(request, "If that email is registered, a code has been sent.")
        return redirect("enter_reset_code")

    return render(request, "registration/request_code.html")


def verify_reset_code(request):
    """Step 2: user enters the 6-digit code they received."""
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        entry = PasswordResetCode.objects.filter(code=code).order_by("-created_at").first()

        if entry and entry.is_valid():
            entry.is_used = True
            entry.save()
            request.session["reset_user_id"] = entry.user.id
            return redirect("set_new_password")

        messages.error(request, "That code is invalid or has expired. Please try again.")
        return redirect("enter_reset_code")

    return render(request, "registration/enter_code.html")


def set_new_password(request):
    """Step 3: user sets a new password, using the session-stored user id."""
    user_id = request.session.get("reset_user_id")
    if not user_id:
        messages.error(request, "Your session expired. Please request a new code.")
        return redirect("request_reset_code")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "registration/set_new_password.html")

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "registration/set_new_password.html")

        user = User.objects.get(id=user_id)
        user.password = make_password(password1)
        user.save()

        del request.session["reset_user_id"]
        messages.success(request, "Your password has been reset. You can now log in.")
        return redirect("login")

    return render(request, "registration/set_new_password.html")