from django.urls import path
from ..views.audit import audit_list

urlpatterns = [
    path("audit/", audit_list, name="audit_list"),
]