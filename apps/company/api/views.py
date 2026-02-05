from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView

from apps.company.infrastructure.models import (
    Company,
    AboutCompany,
    ContactDetail
)
from apps.company.api.serializers import (
    CompanySerializer,
    AboutCompanySerializer,
    ContactDetailSerializer
)


class CompanyAPIView(RetrieveAPIView):
    serializer_class = CompanySerializer

    def get_object(self):
        obj = Company.objects.first()
        if not obj:
            raise NotFound("Company object doesn't exist")
        return obj


class AboutCompanyAPIView(RetrieveAPIView):
    serializer_class = AboutCompanySerializer

    def get_object(self):
        obj = AboutCompany.objects.first()
        if not obj:
            raise NotFound("Company About object doesn't exist")
        return obj


class ContactDetailAPIView(RetrieveAPIView):
    serializer_class = ContactDetailSerializer

    def get_object(self):
        obj = ContactDetail.objects.first()
        if not obj:
            raise NotFound("Company Contact Detail object doesn't exist")
        return obj

