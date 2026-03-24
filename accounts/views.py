from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm
from .models import UserProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                country=form.cleaned_data.get("country", ""),
                occupation=form.cleaned_data.get("occupation", ""),
            )
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})
