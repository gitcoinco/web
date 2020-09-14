from grants.models import *
from dashboard.models import Profile
from grants.utils import get_leaderboard, is_grant_team_member

handles = [
    'mysticryuujin',
]
grant_id = 1101
grant = Grant.objects.get(pk=grant_id)

for handle in handles:
    profile = Profile.objects.filter(handle=handle).first()
    if not profile:
        print(f"{handle} not found")
        continue
    if not is_grant_team_member(grant, profile):
        print(f"adding {handle}")
        grant.team_members.add(profile)
        grant.save()
    else:
        print(f'{handle} is already a team member')

