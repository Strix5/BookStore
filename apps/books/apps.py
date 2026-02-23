from django.apps import AppConfig


class BooksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.books"
    label = "books"

    def ready(self):
        import apps.books.infrastructure.signals
