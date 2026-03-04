from rest_framework import serializers

from apps.company.infrastructure.models import (AboutCompany, Company,
                                                ContactDetail, SocialMedia)
from commons.interfaces.urlfile_path import FileResponseField


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    logo = FileResponseField()

    class Meta:
        model = Company
        fields = ("name", "logo")


class AboutCompanySerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    content = serializers.CharField()
    image = FileResponseField()

    class Meta:
        model = AboutCompany
        fields = ("title", "content", "image")


class SocialMediaSerializer(serializers.ModelSerializer):
    icon = FileResponseField()

    class Meta:
        model = SocialMedia
        fields = ("icon", "link")


class ContactDetailSerializer(serializers.ModelSerializer):
    social_media = SocialMediaSerializer(many=True)

    class Meta:
        model = ContactDetail
        fields = ("phone", "email", "social_media")
