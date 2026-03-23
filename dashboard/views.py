from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from projects.models import Project

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "dashboard/dashboard.html", {"projects": projects})
