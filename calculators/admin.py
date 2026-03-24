from django.contrib import admin
from .models import Budget, Expense, Income


admin.site.register(Budget)
admin.site.register(Income)
admin.site.register(Expense)
