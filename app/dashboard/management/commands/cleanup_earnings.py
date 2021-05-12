from django.core.management.base import BaseCommand

from django.contrib.contenttypes.models import ContentType

from dashboard.models import Earning
from grants.models import Contribution

class Command(BaseCommand):

    help = 'cleans up earnings table for mismatched networks'

    def handle(self, *args, **options):
        # get all contributions made on rinkeby (2590 on prod as of 05/12/2021)
        rinkeby_contributions = Contribution.objects.filter(subscription__network='rinkeby').all()
        # iterate and correct network
        for contribution in rinkeby_contributions:
            # only need to correct if earning table lists mainnet
            earning = Earning.objects.filter(network='mainnet', source_id=contribution.pk).first()
            if earning:
                print("correcting %s" % contribution.pk)
                earning.network = 'rinkeby'
                earning.save()
