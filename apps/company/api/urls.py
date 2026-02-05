from django.urls import path

from apps.company.api.views import (AboutCompanyAPIView, CompanyAPIView,
                                    ContactDetailAPIView)

urlpatterns = (
    path("about_company/", AboutCompanyAPIView.as_view()),
    path("company/", CompanyAPIView.as_view()),
    path("contacts/", ContactDetailAPIView.as_view()),
)
