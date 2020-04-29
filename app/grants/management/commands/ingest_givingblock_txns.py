import pprint
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Activity, Profile
from grants.models import Contribution, Grant, Subscription


class Command(BaseCommand):

    help = 'ingest giving block txns from their partnership with gitcoin grants for round 5'

    def handle(self, *args, **kwargs):
        import csv
        with open('../scripts/input/givingblock_txns.csv', newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:

                #ingest data
                date = row[0]
                grant = row[1]
                _ = row[2]
                currency = row[3]
                amount = row[4]
                txid = row[5]
                user = row[6]
                usd_val = row[7]

                # convert formats
                try:
                    date = date.split(" ")[0]
                    date = timezone.datetime.strptime(date, '%m/%d/%Y')
                    grant = grant.replace('®', '')
                    grant = Grant.objects.get(title__icontains=grant.strip())
                    profile = Profile.objects.get(handle__iexact=user)

                    # create objects
                    validator_comment = ",".join(row)
                    validator_comment = f"created by ingest givingblock_txns script: {validator_comment}"
                    subscription = Subscription()
                    subscription.is_postive_vote = True
                    subscription.active = False
                    subscription.error = True
                    subscription.contributor_address = '/NA'
                    subscription.amount_per_period = amount
                    subscription.real_period_seconds = 2592000
                    subscription.frequency = 30
                    subscription.frequency_unit = 'N/A'
                    subscription.token_address = '0x0'
                    subscription.token_symbol = currency
                    subscription.gas_price = 0
                    subscription.new_approve_tx_id = '0x0'
                    subscription.num_tx_approved = 1
                    subscription.network = 'mainnet'
                    subscription.contributor_profile = profile
                    subscription.grant = grant
                    subscription.comments = validator_comment
                    subscription.amount_per_period_usdt = usd_val
                    subscription.save()

                    contrib = Contribution.objects.create(
                        success=True,
                        tx_cleared=True,
                        tx_override=True,
                        tx_id=txid,
                        subscription=subscription,
                        validator_passed=True,
                        validator_comment=validator_comment,
                        )
                    print(f"ingested {subscription.pk} / {contrib.pk}")

                    metadata = {
                        'id': subscription.id,
                        'value_in_token': str(subscription.amount_per_period),
                        'value_in_usdt_now': str(round(subscription.amount_per_period_usdt,2)),
                        'token_name': subscription.token_symbol,
                        'title': subscription.grant.title,
                        'grant_url': subscription.grant.url,
                        'num_tx_approved': subscription.num_tx_approved,
                        'category': 'grant',
                    }
                    kwargs = {
                        'profile': profile,
                        'subscription': subscription,
                        'grant': subscription.grant,
                        'activity_type': 'new_grant_contribution',
                        'metadata': metadata,
                    }

                    Activity.objects.create(**kwargs)

                except Exception as e:
                    print(e)
