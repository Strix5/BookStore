from rest_framework import serializers

from apps.company.infrastructure.models import (
    Company,
    AboutCompany,
    SocialMedia,
    ContactDetail
)


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Company
        fields = ("name", "logo")


class AboutCompanySerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    content = serializers.CharField()

    class Meta:
        model = AboutCompany
        fields = ("title", "content", "image")


class SocialMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialMedia
        fields = ("icon", "link")


class ContactDetailSerializer(serializers.ModelSerializer):
    social_media = SocialMediaSerializer(many=True)

    class Meta:
        model = ContactDetail
        fields = ("phone", "email", "social_media")
