from django.urls import path
from cms.views import VulnerabilitiesView

urlpatterns = [
    path('vulnerabilities/', VulnerabilitiesView.as_view())
]
