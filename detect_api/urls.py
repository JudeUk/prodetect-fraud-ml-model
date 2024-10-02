
from django.urls import path
from .views import get_all_transactions

urlpatterns = [
    path('transactions/', get_all_transactions, name='get_all_transactions'),
]