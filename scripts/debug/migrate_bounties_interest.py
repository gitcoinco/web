from dashboard.models import Bounty

mock = True
current_bounties = Bounty.objects.filter(current_bounty=True).order_by('-pk')
for current_bounty in current_bounties:
    github_url = current_bounty.github_url
    other_bounties = Bounty.objects.filter(github_url=github_url, current_bounty=False).order_by('-pk')
    if other_bounties.exists():
        didchange = False
        for interested in other_bounties.first().interested.all():
            if interested not in current_bounty.interested.all():
                if not mock:
                    current_bounty.interested.add(interested)
                didchange = True
        if mock:
            if didchange:
                print(f"=========== {github_url} =========")
                print(other_bounties.first().interested.all())
                print(current_bounty.interested.all())
                print("would be changing the bounties for this one right now")
        else:
            current_bounty.save()
