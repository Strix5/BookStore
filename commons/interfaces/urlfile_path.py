from typing import Optional
from urllib.parse import urljoin
from django.conf import settings
from rest_framework import serializers



class FileResponseField(serializers.URLField):

    def __init__(self, is_absolute_url: Optional[bool] = False, **kwargs):
        super().__init__(**kwargs)
        self.is_absolute_url = is_absolute_url

    def to_representation(self, value):
        if not value:
            return None

        request = self.context.get('request')

        try:
            # value is likely a FieldFile (e.g., from FileField or ImageField)
            path = value.url
        except AttributeError:
            path = str(value)

        # Avoid double prefix if already starts with MEDIA_URL
        if path.startswith(settings.MEDIA_URL):
            final_path = path
        else:
            final_path = urljoin(settings.MEDIA_URL, path)

        # Return full URL if request is available
        if self.is_absolute_url and request:
            return request.build_absolute_uri(final_path)
        return final_path
