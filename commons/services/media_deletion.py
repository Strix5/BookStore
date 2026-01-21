import os
from typing import Optional

from django.db.models import Model
from django.db.models.fields.files import FieldFile


def delete_file(path: Optional[str | None]) -> None:
    if not path:
        return
    if not os.path.isfile(path):
        return
    os.remove(path)


def delete_instance_files(instance: Model) -> None:
    for field in instance._meta.get_fields():
        value = getattr(instance, field.name, None)
        if not isinstance(value, FieldFile):
            continue
        if not value:
            continue
        delete_file(value.path)
