from datetime import datetime, timedelta
import pytz
import json
from django.contrib.auth.models import User

from dashboard.models import Profile
from dashboard.models import Bounty
from dashboard.models import Activity
from test_plus.test import TestCase
from django.utils import timezone

class BountiesExploreTest(TestCase):
    """Define tests for the bounties."""

    def setUp(self):
        Bounty.objects.create(
            title='First',
            idx_status=0,
            value_in_token=1,
            token_name='USDT',
            is_open=True,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            raw_data={}
        )
        issue = Bounty.objects.create(
            title='Second',
            idx_status=1,
            value_in_token=2,
            token_name='USDT',
            is_open=True,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=timezone.localtime().replace(tzinfo=None) + timedelta(days=10),
            raw_data={}
        )

        self.current_user = User.objects.create(
            password="asdfasdf", username="asdfasdf")
        current_user_profile = Profile.objects.create(
            user=self.current_user, data={}, hide_profile=False, handle="asdfasdf")

        extend_expiration_activity = Activity.objects.create(activity_type='extend_expiration', profile=current_user_profile)
        issue.activities.add(extend_expiration_activity)
        issue.save()

    def test_bounties_list(self):
        from dashboard.router import BountySerializerSlim
        bounties = Bounty.objects.all()
        serializer = BountySerializerSlim(bounties, many=True)
        assert [el['resurfaced'] for el in serializer.data] == []
