from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render

from .models import GlossaryTerm


def glossary_list(request):
    grouped_terms = {}
    for key, label in GlossaryTerm.TERM_TYPES:
        terms = GlossaryTerm.objects.filter(term_type=key)
        if terms.exists():
            grouped_terms[label] = terms

    return render(
        request,
        "glossary/glossary_list.html",
        {"grouped_terms": grouped_terms},
    )


def glossary_detail(request, slug):
    term = get_object_or_404(GlossaryTerm, slug=slug)
    related_terms = GlossaryTerm.objects.filter(term_type=term.term_type).exclude(id=term.id)[:6]
    return render(
        request,
        "glossary/glossary_detail.html",
        {"term": term, "related_terms": related_terms},
    )


@login_required
@permission_required("main.manage_glossary", raise_exception=True)
def glossary_editor_hub(request):
    glossary_count = GlossaryTerm.objects.count()
    return render(
        request,
        "glossary/editor_hub.html",
        {
            "glossary_count": glossary_count,
            "user_groups": request.user.groups.all(),
        },
    )
