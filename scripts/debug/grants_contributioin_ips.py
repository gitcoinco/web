from django.utils import timezone

from grants.models import *

pk= 600

grant = Grant.objects.get(pk=pk)
profiles = [contribution.subscription.contributor_profile for contribution in grant.contributions]
last_ips = {}
for profile in set(profiles):
    ip = profile.actions.filter(action='Login').order_by('-created_on').first().ip_address
    print(profile.email)
    if ip not in last_ips.keys():
        last_ips[ip] = 0
    last_ips[ip] += 1
for key, val in last_ips.items():
    if val > 1:
        print(key, "created", val, "accounts")
