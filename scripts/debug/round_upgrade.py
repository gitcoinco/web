###############################
# updates amount to 150k
# adds new guest rounds
# for grants round 7
# KO 9/22/2020

increase_rounds = [2,3,4]
increase_to_amount = 150 * 1000
new_round_pot_size = 35 * 1000
new_rounds = [ 'public_goods', 'antisybil']
xfr_grants = {
    'antisybil': [191, 157, 281, 285, 490, 599],
    'public_goods': [1297, 524, 539],
}

#every other param copied from existing rounds

from grants.models import *
from django.db import transaction
with transaction.atomic():
    start_date, end_date = None, None
    total_pot, contribution_multiplier = None, None
    unverified_threshold, verified_threshold = None, None

    for gclr in GrantCLR.objects.filter(pk__in=increase_rounds):
        gclr.total_pot = increase_to_amount
        gclr.save()
        start_date, end_date = gclr.start_date, gclr.end_date
        total_pot, contribution_multiplier = gclr.total_pot, gclr.contribution_multiplier
        unverified_threshold, verified_threshold = gclr.unverified_threshold, gclr.verified_threshold

    for key in new_rounds:
        category = GrantCategory.objects.create(
            category=key.replace('_',' ').title(),
            )
        gt = GrantType.objects.create(
            name=key,
            label=key.replace('_',' ').title(),
            )
        gt.categories.set([category,])
        gt.save()
        GrantCLR.objects.create( 
            is_active=True,
            grant_filters={"grant_type": str(gt.pk)},
            subscription_filters={},
            start_date=start_date,
            end_date=end_date,
            round_num=key,
            unverified_threshold=unverified_threshold,
            verified_threshold=verified_threshold,
            contribution_multiplier=contribution_multiplier,
            total_pot=new_round_pot_size,
            )
        for pk in xfr_grants[key]:
            grant = Grant.objects.get(pk=pk)
            grant.grant_type = gt
            grant.categories.set([category,])
            grant.save()
