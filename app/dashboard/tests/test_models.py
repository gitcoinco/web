from datetime import datetime, timedelta

from django.test import TestCase

from dashboard.models import Bounty


class BountyTest(TestCase):
    """ Test module for Bounty model """

    def setUp(self):
        Bounty.objects.create(
            current_bounty=True,
            title='Gitcoin Bounty',
            web3_created=datetime.now() - timedelta(minutes=10),
            value_in_token=0.01,
            token_address='0xe635c6d338dcd31c979b88000ff97c1fa3f0472c', # GIT token
            github_url='https://github.com/gitcoinco/web/issues/232',
            expires_date=datetime.now(),
            is_open=True,
            raw_data = {}
        )

    def test_github_repository(self):
        bounty = Bounty.objects.get(title='Gitcoin Bounty')
        self.assertEqual(bounty.github_repository, 'gitcoinco/web')
