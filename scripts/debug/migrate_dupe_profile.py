old_username='x'
new_username='y'
from dashboard.management.commands import cleanup_dupe_profiles
from dashboard.models import Profile

old_profile = Profile.objects.get(handle__iexact=old_username)
new_profile = Profile.objects.get(handle__iexact=new_username)

user = old_profile.user
user.username = new_username
user.save()

new_profile.user = old_profile.user
old_profile.user = None
old_profile.save()
new_profile.save()

cleanup_dupe_profiles.combine_profiles(old_profile, new_profile)
