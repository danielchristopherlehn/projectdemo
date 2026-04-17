from django.contrib import admin
from .models import LoanData, MortgageData, RentVsOwnData

# Register your models here so they appear in the Django admin panel
admin.site.register(LoanData)
admin.site.register(MortgageData)
admin.site.register(RentVsOwnData)
