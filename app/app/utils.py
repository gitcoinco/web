from django.conf import settings
from dashboard.models import Bounty, Profile
from app.github import get_user
from django.utils import timezone


def sync_profile(handle):
    data = get_user(handle)
    is_error = not 'name' in data.keys()
    if is_error:
        print("- error main")
        return

    repos_data = get_user(handle, '/repos')

    # store the org info in postgres
    org, _ = Profile.objects.get_or_create(
        handle=handle,
        defaults = {
            'last_sync_date': timezone.now(),
            'data': data,
            'repos_data': repos_data,
        },
        )
    org.handle = handle
    org.data = data
    org.repos_data = repos_data
    org.save()
    print("- updated")
