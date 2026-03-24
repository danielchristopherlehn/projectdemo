from django.urls import path
from . import views

urlpatterns = [
    path("", views.glossary_list, name="glossary_list"),
    path("editor/", views.glossary_editor_hub, name="glossary_editor_hub"),
    path("<slug:slug>/", views.glossary_detail, name="glossary_detail"),
]
