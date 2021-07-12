from grants.models import Grant

from .models import Offer


def is_user_townsquare_enabled(user):
    if not user.is_authenticated:
        return False

    # roll out emails to 20% of userbase to start. see if we get blowback
    # KO 6/2/2020 - we got no complaints about the daily email yesterday, so upping to 40%
    # KO 6/3/2020, upping to 55%
    # KO 7/30/2020, upping to 100%

    if user.pk % 100 < 101:
        return True

    if user.is_staff:
        return True

    return True


def can_pin(request, what):
    permission = False
    # handle permissions for pinning/unpinning
    if ':' in what:
        split = what.split(':')
        key = split[0]
        lookup = split[1]
    else:
        key = what
        lookup = what

    if key == 'grant':  # check for grant owner

        permission = request.user.is_authenticated and Grant.objects.filter(
            team_members__handle__in=[request.user.profile.handle]).exists()

    elif key == 'tribe':  # check for org owner
        permission = request.user.is_authenticated and any(
            [lookup.lower() == org.lower() for org in request.user.profile.organizations])
    elif key == 'my_threads':
        permission = False
    elif key in ['search-announce', 'search-mentor', 'search-jobs', 'search-bounty', 'search-help', 'search-meme', 'search-music', 'search-other']:
        if request.user.is_staff:
            permission = True

    else:
        if request.user.is_staff:
            permission = True

    return permission


def is_email_townsquare_enabled(email):
    from django.contrib.auth.models import User
    user = User.objects.filter(email=email).first()
    if not user:
        return False
    return is_user_townsquare_enabled(user)
