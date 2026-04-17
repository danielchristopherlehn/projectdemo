from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


@login_required
def project_list(request):
    projects = Project.objects.filter(
        user=request.user
    ).select_related('linked_asset').order_by('-created_at')
    return render(request, "projects/project_list.html", {"projects": projects})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect("project_detail", project_id=project.id)
    else:
        form = ProjectForm(user=request.user)
    return render(request, "projects/create_project.html", {"form": form})


@require_POST
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    project.delete()
    return redirect("project_list")


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if project.calculator_type == "loan":
        return redirect("calculators:loan", project_id=project.id)
    elif project.calculator_type == "mortgage":
        return redirect("calculators:mortgage", project_id=project.id)
    elif project.calculator_type == "rent_vs_own":
        return redirect("calculators:rent_vs_own", project_id=project.id)
    else:
        messages.error(request, "Unknown calculator type.")
        return redirect("project_list")
