from django.urls import path
from sanctions.views import sanctions_search_view


urlpatterns = [
    path('search/', sanctions_search_view, name='sanctions_search'),
]