from apps.users.infrastructure.models import Profile


def get_profile():
    return Profile.objects.select_related("user")


