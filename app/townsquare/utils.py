
def is_user_townsquare_enabled(user):
    if not user.is_authenticated:
        return False

    if user.is_staff:
        return True

    if user.groups.filter(name='townsquare').exists():
        return True

    return False


def is_email_townsquare_enabled(email):
    from django.contrib.auth.models import User
    user = User.objects.filter(email=email).first()
    if not user:
        return False
    return is_user_townsquare_enabled(user)


