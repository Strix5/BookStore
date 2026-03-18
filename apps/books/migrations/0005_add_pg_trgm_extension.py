from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0004_book_in_stock"),
    ]

    operations = [
        TrigramExtension(),
    ]