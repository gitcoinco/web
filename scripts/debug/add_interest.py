github_url = 'https://github.com/gitcoinco/web/issues/380'
username = 'iliketobuildstuff'

from dashboard.models import Profile, Interest, Bounty
bounty = Bounty.objects.get(current_bounty=True, github_url=github_url)
profile = Profile.objects.filter(handle=username).first()
interest = Interest.objects.get_or_create(profile=profile)
bounty.interested.add(interest[0])


