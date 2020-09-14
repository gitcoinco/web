from grants.models import *
from dashboard.models import Profile
from grants.utils import get_leaderboard, is_grant_team_member

handles = [
    'barnabemonnot',
    'poojaranjan',
    'timbeiko',
    'danfinaly',
    'madeoftin',
]
grant_id = 946
grant = Grant.objects.get(pk=946)

for handle in handles:
    profile = Profile.objects.get(handle=handle)
    if not is_grant_team_member(grant, profile):
        grant.team_members.add(profile)
        grant.save()
    print(profile)

