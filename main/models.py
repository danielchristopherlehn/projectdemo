from django.db import models


class GlossaryTerm(models.Model):
    TERM_TYPES = [
        ("loan", "Loan"),
        ("mortgage", "Mortgage"),
        ("budget", "Budget"),
        ("housing", "Housing"),
        ("general", "General Finance"),
    ]

    term_type = models.CharField(max_length=50, choices=TERM_TYPES, default="general")
    term = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    definition = models.TextField()

    class Meta:
        ordering = ["term"]
        permissions = [
            ("manage_glossary", "Can manage glossary content"),
        ]

    def __str__(self):
        return self.term
