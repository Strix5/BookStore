from django.apps import AppConfig


class GalleriesConfig(AppConfig):
    name = "apps.gallery"

    def ready(self):
        import apps.gallery.infrastructure.signals
