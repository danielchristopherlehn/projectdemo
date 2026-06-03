from django.contrib.auth import login
from django.db import IntegrityError
from django.shortcuts import redirect, render

from .forms import RegisterForm
from .models import UserProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                UserProfile.objects.create(
                    user=user,
                    country=form.cleaned_data.get("country", ""),
                    occupation=form.cleaned_data.get("occupation", ""),
                )
                login(request, user)
                return redirect("dashboard")
            except IntegrityError:
                # Username already exists — show a clear error on the form
                form.add_error("username", "That username is already taken. Please choose another.")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})
