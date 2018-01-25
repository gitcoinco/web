import json
from datetime import datetime, timedelta

from django.test import Client, TestCase
from django.urls import reverse

from dashboard.models import Bounty
from dashboard.router import BountySerializer
from freezegun import freeze_time
from rest_framework import status

# initialize the API Client app
client = Client()


class GetAllBountiesTest(TestCase):
    """ Test module for GET all bounties API """

    def setUp(self):
        # gitcoin/web bounty
        Bounty.objects.create(
            current_bounty=True,
            title='Gitcoin Bounty 1',
            web3_created=datetime.now(),
            value_in_token=0.01,
            token_address='0xe635c6d338dcd31c979b88000ff97c1fa3f0472c', # GIT token
            github_url='https://github.com/gitcoinco/web/issues/1',
            expires_date=datetime.now(),
            is_open=True,
            raw_data = {}
        )

        # gitcoin/web bounty
        Bounty.objects.create(
            current_bounty=True,
            title='Gitcoin Bounty 2',
            web3_created=datetime.now() - timedelta(minutes=5),
            value_in_token=0.01,
            token_address='0xe635c6d338dcd31c979b88000ff97c1fa3f0472c', # GIT token
            github_url='https://github.com/gitcoinco/web/issues/232',
            expires_date=datetime.now(),
            is_open=True,
            raw_data = {}
        )

        # non gitcoin/web bounty
        Bounty.objects.create(
            current_bounty=True,
            title='FooBar Bounty 1',
            web3_created=datetime.now() - timedelta(minutes=10),
            value_in_token=0.01,
            token_address='0xe635c6d338dcd31c979b88000ff97c1fa3f0472c', # GIT token
            github_url='https://github.com/foo/bar/issues/1',
            expires_date=datetime.now(),
            is_open=True,
            raw_data = {}
        )

    # FreezeGun required due to now property on Bounties
    @freeze_time('1999-12-31')
    def test_get_all_bounties_with_github_repository(self):
        response = client.get('/api/v0.1/bounties/?github_repository=gitcoinco%2Fweb&order_by=web3_created')
        bounties = Bounty.objects.filter(title__startswith='Gitcoin Bounty').order_by('web3_created')
        serializer = BountySerializer(bounties, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
