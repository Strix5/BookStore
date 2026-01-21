from django.utils.text import slugify
from unidecode import unidecode


def generate_slug(instance, model_class, slug_attribute):
    if hasattr(instance, "slug"):
        if hasattr(instance, "safe_translation_getter"):
            title = instance.safe_translation_getter(slug_attribute, any_language=True)
        else:
            title = getattr(instance, slug_attribute, None)

        if title:
            title_transliterated = unidecode(title)  # Cyrillic -> Latin
            base_slug = slugify(title_transliterated)
            slug = base_slug
            counter = 1

            if model_class._meta.get_field("slug").unique:
                while (
                    model_class.objects.filter(slug=slug)
                    .exclude(pk=instance.pk)
                    .exists()
                ):
                    slug = f"{base_slug}-{counter}"
                    counter += 1

            instance.slug = slug
