from django.urls import path
from . import views


urlpatterns = [
    path("create/", views.create_project, name="create_project"),
    path("<int:project_id>/", views.project_detail, name="project_detail"),
    path("<int:project_id>/delete/", views.delete_project, name="delete_project"),
]

urlpatterns = [
    path('create/', views.create_project, name='create_project'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
]

from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_project, name="create_project"),
    path("<int:project_id>/delete/", views.delete_project, name="delete_project"),
    path("<int:project_id>/", views.project_detail, name="project_detail"),
]