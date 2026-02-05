from apps.company.infrastructure.models import (AboutCompany, Company,
                                                ContactDetail)


def get_company_object() -> Company:
    return Company.objects.first()


def get_about_company_object() -> AboutCompany:
    return AboutCompany.objects.first()


def get_contact_object() -> ContactDetail:
    return ContactDetail.objects.first()

