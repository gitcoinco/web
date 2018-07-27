# -*- coding: utf-8 -*-
"""Handle dashboard notification related tests.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from datetime import datetime

from dashboard.models import Bounty, Profile, BountyFulfillment, Interest, Activity
from dashboard.notifications import amount_usdt_open_work, append_snooze_copy, build_github_notification
from pytz import UTC
from test_plus.test import TestCase


class DashboardNotificationsTest(TestCase):
    """Define tests for dashboard notifications."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3e18,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=UTC),
            github_url='https://github.com/gitcoinco/web/issues/11',
            token_address='0x0000000000000000000000000000000000000000',
            issue_description='hello world',
            bounty_owner_github_username='samplegitcoindeveloper1',
            bounty_owner_profile= Profile.objects.filter(handle='samplegitcoindeveloper1').first(),
            is_open=True,
            accepted=False,
            permission_type='permissionless',
            expires_date=datetime(2008, 11, 30, tzinfo=UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        self.natural_value = round(self.bounty.get_natural_value(), 4)
        self.usdt_value = f"({round(self.bounty.value_in_usdt, 2)} USD)" if self.bounty.value_in_usdt else ""
        self.absolute_url = self.bounty.get_absolute_url()
        self.amount_open_work = amount_usdt_open_work()
        self.bounty_owner = f"(@{self.bounty.bounty_owner_github_username})"

    def test_build_github_notification_new_bounty_traditional_permissionless(self):
        message = build_github_notification(self.bounty, 'new_bounty')
        print(message)
        absolute_url = self.bounty.get_absolute_url()
        assert f"Funding: " in message 
        assert f"ETH "
        assert f"USD @" in message
        assert f"Start work on this issue on the Gitcoin issue details page" in message
        assert f"{absolute_url}" in message
        assert f"Looking for another project? ${self.amount_open_work} more funded OSS work available on the [Gitcoin Issue Explorer]" in message
        assert f"Questions Checkout [Gitcoin Help](gitcoin_help_url) or [Gitcoin Slack](gitcoin_slack_url)" in message
        
    def test_build_github_notification_new_bounty_traditional_approval(self):
        self.bounty.bounty_type = 'traditional'
        self.bounty.permission_type='approval'
        message = build_github_notification(self.bounty, 'new_bounty')
        print(message)
        assert f"Funding: {self.bounty.get_natural_value} ETH ({self.bounty.value_in_usdt_now}) USD @" in message
        assert f"Express interest to work on this issue on the Gitcoin issue details page" in message
        assert f"{bounty.github_url}" in message
        assert f"Looking for another project? ${self.amount_open_work} more funded OSS work available on the [Gitcoin Issue Explorer]" in message
        assert f"Questions Checkout [Gitcoin Help](gitcoin_help_url) or [Gitcoin Slack](gitcoin_slack_url)" in message

    def test_build_github_notification_new_bounty_cooperative(self):
        self.bounty.bounty_type = 'cooperative'
        self.bounty.permission_type = 'permissionless'
        message = build_github_notification(self.bounty, 'new_bounty')
        print(message)
        assert f"Funding: {self.bounty.get_natural_value} ETH ({self.bounty.value_in_usdt_now}) USD @" in message
        assert f"Start work on this issue on the Gitcoin issue details page" in message
        assert f"{bounty.github_url}" in message
        assert f"Looking for another project? ${self.amount_open_work} more funded OSS work available on the [Gitcoin Issue Explorer]" in message
        assert f"Questions Checkout [Gitcoin Help](gitcoin_help_url) or [Gitcoin Slack](gitcoin_slack_url)" in message

    def test_build_github_notification_new_bounty_contest(self):
        self.bounty.bounty_type = 'contest'
        self.bounty.permission_type='permissionless'
        message = build_github_notification(self.bounty, 'new_bounty')
        print(message)
        assert f"Funding: {self.bounty.get_natural_value} ETH ({self.bounty.value_in_usdt_now}) USD @" in message
        assert f"Start work on this issue on the Gitcoin issue details page" in message
        assert f"{bounty.github_url}" in message
        assert f"Looking for another project? ${self.amount_open_work} more funded OSS work available on the [Gitcoin Issue Explorer]" in message
        assert f"Questions Checkout [Gitcoin Help](gitcoin_help_url) or [Gitcoin Slack](gitcoin_slack_url)" in message


    def test_build_github_notification_new_bounty(self):
        """Test the dashboard helper build_github_notification method with new_bounty."""
        message = build_github_notification(self.bounty, 'new_bounty')
        print(message)
        assert f'__This issue now has a funding of {self.natural_value} {self.bounty.token_name}' in message
        assert self.usdt_value in message
        assert f'This issue now has a funding of' in message
        assert f'${self.amount_open_work}' in message

    def test_build_github_notification_express_interest_traditional_approval(self):
        self.bounty.bounty_type = 'traditional'
        self.bounty.permission_type='approval'
        interest_profile = Profile.objects.filter(handle='samplegitcoindeveloper2').first()
        interest = Interest.objects.create(
               profile=interest_profile,
               issue_message='hello world',
               pending=True
        )
        self.bounty.interested.add(interest)
        message = build_github_notification(self.bounty, 'work_started')
        bounty_approve_worker_url = bounty.approve_worker_url(interest_profile.handle)
        bounty_reject_worker_url = bounty.reject_worker_url(interest_profile.handle)
        print(message)
        assert f'[@{interest_profile.handle}]({ interest_profile.url }) has __expressed interest__ in this project.' in message
        assert f'[@{ self.bounty.bounty_owner_profile.handle }]({ self.bounty.bounty_owner_profile.url }), [Approve Worker]({ bounty_approve_worker_url }) | [Reject Worker]({ bounty_reject_worker_url })' in message

    def test_build_github_notification_start_work_traditional_permissionless(self):
        self.bounty.bounty_type='traditional'
        self.bounty.permission_type='permissionless'
        interest_profile = Profile.objects.filter(handle='samplegitcoindeveloper2').first()
        interest = Interest.objects.create(
               profile=interest_profile,
               issue_message='hello world',
               pending=False,
               acceptance_date=datetime(2018, 11, 30, tzinfo=UTC)
        )
        self.bounty.interested.add(interest)
        message = build_github_notification(self.bounty, 'work_started')
        print(message)
        assert f'[@{ interest_profile.handle }]({ interest_profile.url }) has __started work__ on this project.' in message
        self.bounty.interested.remove(interest)

    def test_build_github_notification_start_work_traditional_approval(self):
        self.bounty.bounty_type='traaditional'
        self.bounty.permission_type='approval'
        interest_profile = Profile.objects.filter(handle='samplegitcoindeveloper2').first()
        interest = Interest.objects.create(
               profile=interest_profile,
               issue_message='hello world',
               pending=False,
               acceptance_date=datetime(2018, 11, 30, tzinfo=UTC)
        )
        self.bounty.interested.add(interest)
        message = build_github_notification(self.bounty, 'work_started')
        print(message)
        assert f'[@{ interest_profile.handle }]({ interest_profile.url }) has been __approved__ to start work on this project.'
        self.bounty.interested.remove(interest)

    def test_build_github_notification_start_work_cooperative(self):
        self.bounty.bounty_type='cooperative'
        self.bounty.permission_type='permissionless'
        interest_profile = Profile.objects.filter(handle='oogetyboogety').first()
        interest_profile2 = Profile.objects.filter(handle='oogetyboogety').first()
        interest = Interest.objects.create(
               profile=interest_profile,
               issue_message='hello world',
               pending=False,
               acceptance_date=datetime(2018, 11, 30, tzinfo=UTC)
        )
        self.bounty.interested.add(interest)
        interest2 = Interest.objects.create(
               profile=interest_profile2,
               issue_message='hello world 2',
               pending=False,
               acceptance_date=datetime(2018, 11, 31, tzinfo=UTC)
        )
        self.bounty.interested.add(interest2)
        message = build_github_notification(self.bounty, 'work_started')
        print(message)
        assert f'[@{ interest_profile.handle }]({ interest_profile.url }) has __started work__ on this project.' in message
        assert f'Comments: hello world' in message
        assert f'[@{ interest_profile2.handle }]({ interest_profile2.url }) has __started work__ on this project.' in message
        assert f'Comments: hello world 2' in message
        self.bounty.interested.remove(interest)
        self.bounty.interested.remove(interest2)

    def test_build_github_notification_start_work_contest(self):
        self.bounty.bounty_type='contest'
        self.bounty.permission_type='permissionless'
        interest = Interest.objects.create(
               profile=Profile.objects.filter(handle='samplegitcoindeveloper1').first(),
               issue_message='hello world',
               pending=False,
               acceptance_date=datetime(2018, 11, 30, tzinfo=UTC)
        )
        self.bounty.interested.add(interest)
        message = build_github_notification(self.bounty, 'work_started')
        print(message)
        assert f'[@{ interest_profile.handle }]({ interest_profile.url }) has __started work__ on this project.' in message
        assert f'Comments: helo world' in message
        self.bounty.interested.remove(interest)

    def test_build_github_notification_stop_work_contest(self):
        self.bounty.bounty_type='traditional'
        self.bounty.permission_type='permissionless'
        activity_profile = Profile.objects.filter(handle='samplegitcoindeveloper1').first()
        activity = Activity.objects.create(
               profile=activity_profile,
               activity_type='stop_work',
               bounty=self.bounty)
        self.bounty.activities.add(activity)
        interest_profile = Profile.objects.filter(handle='samplegitcoindeveloper2').first()
        interest = Interest.objects.create(
               profile=interest_profile,
               issue_message='hello world',
               pending=False,
               acceptance_date=datetime(2018, 11, 30, tzinfo=UTC)
        )
        self.bounty.interested.add(interest)
        message = build_github_notification(self.bounty, 'stop_work')
        print(message)
        assert f'[@{ activity_profile.handle }]({ activity_profile.url }) has __stopped work__ on this project.' in message
        assert f'[@{ interest_profile.handle }]({ interest_profile.url }) is __still working__ on this project.' in message

    def test_build_github_notification_submit_work_traditional_permissionless(self):
        self.bounty.bounty_type='traditional'
        self.bounty.permission_type='permissionless'
        fulfillment_profile = Profile.objects.filter(handle='samplegitcoindeveloper1').first()
        fulfillment = BountyFulfillment.objects.create(
              fulfiller_address='0x0000000000000000000000000000000000000000',
              fulfiller_email='gitcointestdeveloper1@gmail.com',
              fulfiller_github_username='samplegitcoindeveloper1',
              fulfiller_github_url='http://gitoin.com/samplegitcoindeveloper1',
              bounty=self.bounty,
              profile=fulfillment_profile,
              accepted=False
        )
        self.bounty.fulfillments.add(fulfillment)
        message = build_github_notification(self.bounty, 'work_submitted')
        print(message)
        assert f'[@{fulfillment_profile.handle}]({ fulfillment_profile.url }) has __submitted work__ for this project.'
        self.bounty.fulfillments.remove(fulfillment)

    def test_build_github_notification_submit_work_traditional_approval(self):
        self.bounty.bounty_type='traditional'
        self.bounty.permission_type='approval'
        fulfillment_profile = Profile.objects.filter(handle='samplegitcoindeveloper1').first()
        fulfillment = BountyFulfillment.objects.create(
              fulfiller_address='0x0000000000000000000000000000000000000000',
              fulfiller_email='gitcointestdeveloper1@gmail.com',
              fulfiller_github_username='samplegitcoindeveloper1',
              fulfiller_github_url='http://gitoin.com/samplegitcoindeveloper1',
              bounty=self.bounty,
              profile=fulfillment_profile,
              accepted=False
        )
        message = build_github_notification(self.bounty, 'work_submitted')
        print(message)
        assert f'[@{fulfillment_profile.handle}]({ fulfillment_profile.url }) has __submitted work__ for this project.'
        self.bounty.fulfillments.remove(fulfillment)

    def test_build_github_notification_submit_work_cooperative(self):
        self.bounty.bounty_type='cooperative'
        self.bounty.permission_type='permissionless'
        message = build_github_notification(self.bounty, 'work_submitted')
        fulfillment_profile = Profile.objects.filter(handle='samplegitcoindeveloper1').first()
        fulfillment = BountyFulfillment.objects.create(
              fulfiller_address='0x0000000000000000000000000000000000000000',
              fulfiller_email='gitcointestdeveloper1@gmail.com',
              fulfiller_github_username='samplegitcoindeveloper1',
              fulfiller_github_url='http://gitoin.com/samplegitcoindeveloper1',
              bounty=self.bounty,
              profile=fulfillment_profile,
              accepted=False
        )
        message = build_github_notification(self.bounty, 'work_submitted')
        print(message)
        assert f'[@{fulfillment_profile.handle}]({ fulfillment_profile.url }) has __submitted work__ for this project.'
        self.bounty.fulfillments.remove(fulfillment)

    def test_build_github_notification_accept_work_traditional_permissionless(self):
        self.bounty.bounty_type='traditional'
        self.bounty.permission_type='permissionless'
        fulfillment_profile = Profile.objects.filter(handle='samplegitcoindeveloper1').first()
        fulfillment = BountyFulfillment.objects.create(
              fulfiller_address='0x0000000000000000000000000000000000000000',
              fulfiller_email='gitcointestdeveloper1@gmail.com',
              fulfiller_github_username='samplegitcoindeveloper1',
              fulfiller_github_url='http://gitoin.com/samplegitcoindeveloper1',
              bounty=self.bounty,
              profile=fulfillment_profile,
              accepted=True
        )
        self.bounty.fulfillments.add(fulfillment)
        message = build_github_notification(self.bounty, 'work_done')
        print(message)
        assert f'[@{ self.bounty.bounty_owner_github_username }]({ self.bounty.bounty_owner_profile_url }) has __accepted work __ from [@{ fulfillment.fulfiller_github_usernaem }]({ fulfillment.fulfiller_github_url }).'
        self.bounty.fulfillments.remove(fulfillment)

    def test_build_github_notification_accept_work_traditional_approval(self):
        self.bounty.bounty_type='traditional'
        self.bounty.permission_type='permissionless'
        fulfillment_profile = Profile.objects.filter(handle='samplegitcoindeveloper1').first()
        fulfillment = BountyFulfillment.objects.create(
              fulfiller_address='0x0000000000000000000000000000000000000000',
              fulfiller_email='gitcointestdeveloper1@gmail.com',
              fulfiller_github_username='samplegitcoindeveloper1',
              fulfiller_github_url='http://gitoin.com/samplegitcoindeveloper1',
              bounty=self.bounty,
              profile=fulfillment_profile,
              accepted=True
        )
        self.bounty.fulfillments.add(fulfillment)
        message = build_github_notification(self.bounty, 'work_done')
        print(message)
        assert f'[@{ self.bounty.bounty_owner_github_username }]({ self.bounty.bounty_owner_profile_url }) has __accepted work __ from [@{ fulfillment.fulfiller_github_usernaem }]({ fulfillment.fulfiller_github_url }).'
        self.bounty.fulfillments.remove(fulfillment)

    def test_build_github_notification_accept_work_cooperative(self):
        self.bounty.bounty_type='traditional'
        self.bounty.permission_type='approval'
        fulfillment_profile = Profile.objects.filter(handle='samplegitcoindeveloper1').first()
        fulfillment = BountyFulfillment.objects.create(
              fulfiller_address='0x0000000000000000000000000000000000000000',
              fulfiller_email='gitcointestdeveloper1@gmail.com',
              fulfiller_github_username='samplegitcoindeveloper1',
              fulfiller_github_url='http://gitoin.com/samplegitcoindeveloper1',
              bounty=self.bounty,
              profile=fulfillment_profile,
              accepted=True
        )
        self.bounty.fulfillments.add(fulfillment)
        message = build_github_notification(self.bounty, 'work_done')
        print(message)
        assert f'[@{ self.bounty.bounty_owner_github_username }]({ self.bounty.bounty_owner_profile_url }) has __accepted work __ from [@{ fulfillment.fulfiller_github_usernaem }]({ fulfillment.fulfiller_github_url }).'
        self.bounty.fulfillments.remove(fulfillment)

    def test_build_github_notification_accept_work_contest(self):
        self.bounty.bounty_type='cooperativve'
        self.bounty.permission_type='permissionless'
        fulfillment_profile = Profile.objects.filter(handle='samplegitcoindeveloper1').first()
        fulfillment = BountyFulfillment.objects.create(
              fulfiller_address='0x0000000000000000000000000000000000000000',
              fulfiller_email='gitcointestdeveloper1@gmail.com',
              fulfiller_github_username='samplegitcoindeveloper1',
              fulfiller_github_url='http://gitoin.com/samplegitcoindeveloper1',
              bounty=self.bounty,
              profile=fulfillment_profile,
              accepted=True
        )
        self.bounty.fulfillments.add(fulfillment)
        message = build_github_notification(self.bounty, 'work_done')
        print(message)
        assert f'[@{ self.bounty.bounty_owner_github_username }]({ self.bounty.bounty_owner_profile_url }) has __accepted work __ from [@{ fulfillment.fulfiller_github_usernaem }]({ fulfillment.fulfiller_github_url }).'
        self.bounty.fulfillments.remove(fulfillment)


    def test_build_github_notification_killed_bounty(self):
        """Test the dashboard helper build_github_notification method with killed_bounty."""
        message = build_github_notification(self.bounty, 'killed_bounty')
        assert f"__The funding of {self.natural_value} {self.bounty.token_name} {self.usdt_value}" in message
        assert 'Questions?' in message
        assert f'${self.amount_open_work}' in message

    def test_build_github_notification_increased_bounty(self):
        """Test the dashboard helper build_github_notification method with new_bounty."""
        message = build_github_notification(self.bounty, 'increased_bounty')
        assert f'__The funding of this issue was increased to {self.natural_value} {self.bounty.token_name}' in message
        assert self.usdt_value in message
        assert f'The funding of this issue was increased' in message
        assert f'${self.amount_open_work}' in message

    def test_append_snooze_copy(self):
        """Test the dashboard notification utility append_snooze_copy."""
        snooze_copy = append_snooze_copy(self.bounty)
        segments = snooze_copy.split(' | ')
        assert len(segments) == 5
        for i, day in enumerate([1, 3, 5, 10, 100]):
            plural = "s" if day != 1 else ""
            copy = f'[{day} day{plural}]({self.bounty.snooze_url(day)})'
            if day == 1:
                copy = f'\nFunders only: Snooze warnings for {copy}'
            assert segments[i] == copy

    def tearDown(self):
        """Perform cleanup for the testcase."""
        self.bounty.delete()
