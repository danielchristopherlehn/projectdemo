from django.contrib import admin
from .models import GlossaryTerm


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ("term", "term_type", "slug")
    list_filter = ("term_type",)
    search_fields = ("term", "definition", "slug")
