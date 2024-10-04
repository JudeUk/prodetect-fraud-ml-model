"""
URL configuration for prodetectBackendDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from detect_api.views import predict_transaction 
from detect_api.views import get_all_transactions
from restrictionRules.views import *
from sanctions.views import sanctions_search_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('predict/', predict_transaction, name='predict_transaction'),
     path('api/', include('detect_api.urls')),
        path('create-rule/', create_rule, name='create_rule'),
    path('activate-rule/<int:rule_id>/', activate_rule, name='activate_rule'),
    path('deactivate-rule/<int:rule_id>/', deactivate_rule, name='deactivate_rule'),
    path('delete-rule/<int:rule_id>/', delete_rule, name='delete_rule'),
    path('suspended-transactions/', view_suspended_transactions, name='view_suspended_transactions'),
    path('check-transaction/', check_transaction, name='check_transaction'),  # New view to check transactions
    path('manage-transaction/<int:transaction_id>/', manage_transaction, name='manage_transaction'),  # New view to manage transactions on hold
    path('sanctions/', include('sanctions.urls'))
]





