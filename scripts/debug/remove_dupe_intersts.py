from dashboard.models import Bounty

mock = True
current_bounties = Bounty.objects.filter(current_bounty=True).order_by('-pk')
for current_bounty in current_bounties:
    already_exists = []
    for interested in current_bounty.interested.all():
        if str(interested) in already_exists:
            interested.delete()
            print(f"deleting {interested} from {current_bounty.github_url}")
        else:
            already_exists.append(str(interested))
    # print(current_bounty.interested.all())
