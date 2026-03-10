from django.apps import AppConfig


class GalleriesConfig(AppConfig):
    name = "apps.galleries"

    def ready(self):
        import apps.galleries.infrastructure.signals
