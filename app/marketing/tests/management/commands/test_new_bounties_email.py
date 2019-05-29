from datetime import datetime, timedelta

from django.core.management import call_command
from django.utils import timezone

import pytest
from dashboard.models import Bounty, Profile
from marketing.management.commands.new_bounties_email import get_bounties_for_keywords
from marketing.models import Keyword
from test_plus.test import TestCase


@pytest.mark.django_db
class TestNewBountiesEmail(TestCase):
    """Define tests for testing new bounties email."""
    
    def setUp(self):
        """Perform setup for the testcase."""
        
        Profile.objects.create(
            data={},
            handle='fred',
            email='fred@localhost'
        )
        Bounty.objects.create(
            title='Python foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=timezone.now(),
            github_url='https://github.com/gitcoinco/web',
            token_address='0x0',
            issue_description='Python test',
            bounty_owner_github_username='john',
            is_open=True,
            accepted=True,
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            bounty_owner_email='john@bar.com',
            current_bounty=True,
            network='mainnet',
            bounty_reserved_for_user=Profile.objects.filter(handle__iexact='fred').first(),
        )

        Bounty.objects.create(
            title='Python 2 foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=timezone.now(),
            github_url='https://github.com/ethereum/solidity',
            token_address='0x0',
            issue_description='Test Python 2',
            bounty_owner_github_username='jack',
            is_open=True,
            accepted=True,
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            bounty_owner_email='jack@bar.com',
            current_bounty=True,
            network='mainnet',
        )


    def test_get_bounties_for_keywords(self):
        """Test get_bounties_for_keywords function to confirm a bounty reserved for a specific user is excluded."""
        new_bounties, _all_bounties = get_bounties_for_keywords('Python',24)
        assert new_bounties.count() == 1
