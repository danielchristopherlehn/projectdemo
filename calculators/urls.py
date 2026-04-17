from django.urls import path
from . import views

app_name = 'calculators'

urlpatterns = [
    path('loan/<int:project_id>/', views.loan_calculator_view, name='loan'),
    path('mortgage/<int:project_id>/',
         views.mortgage_calculator_view, name='mortgage'),
    path('rent-vs-own/<int:project_id>/',
         views.rent_vs_own_calculator_view, name='rent_vs_own'),
]
