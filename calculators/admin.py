from django.contrib import admin
from .models import LoanData, MortgageData, RentVsOwnData

admin.site.register(LoanData)
admin.site.register(MortgageData)
admin.site.register(RentVsOwnData)
