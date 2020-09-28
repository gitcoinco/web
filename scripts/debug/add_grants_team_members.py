from dashboard.models import Profile
from grants.models import *
from grants.utils import get_leaderboard, is_grant_team_member

handles = [
    'adamstallard',
    'alirezapaslar',
]
grant_id = 191
grant = Grant.objects.get(pk=grant_id)

for handle in handles:
    profile = Profile.objects.filter(handle__iexact=handle).first()
    if not profile:
        print(f"{handle} not found")
        continue
    if not is_grant_team_member(grant, profile):
        print(f"adding {handle}")
        grant.team_members.add(profile)
        grant.save()
    else:
        print(f'{handle} is already a team member')
