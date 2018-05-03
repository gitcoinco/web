from dashboard.models import Bounty, Interest, Profile

github_url = 'https://github.com/ethgasstation/ethgasstation-api/issues/1'
username = 'eswarasai'

bounty = Bounty.objects.get(current_bounty=True, github_url=github_url)
profile = Profile.objects.filter(handle=username).first()
interest = Interest.objects.create(profile_id=profile.pk)

bounty.interested.add(interest[0])
