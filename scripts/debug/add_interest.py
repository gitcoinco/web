github_url = 'https://github.com/ethgasstation/ethgasstation-api/issues/1'
username = 'eswarasai'

from dashboard.models import Bounty, Interest, Profile

bounty = Bounty.objects.get(current_bounty=True, github_url=github_url)
profile = Profile.objects.filter(handle=username).first()
try:
    interest = Interest.objects.get_or_create(profile=profile)
except Interest.MultipleObjectsReturned:
    interest = Interest.objects.filter(profile=profile)

bounty.interested.add(interest[0])
