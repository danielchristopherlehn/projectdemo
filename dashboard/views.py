from django.shortcuts import render
from projects.models import Project


def dashboard(request):

    projects = Project.objects.filter(user=request.user)

    return render(request, "dashboard/dashboard.html", {
        "projects": projects
    } )
