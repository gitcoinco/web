import pytest
from dashboard.models import Profile
from dashboard.tests.factories.bounty_factory import BountyFactory
from dashboard.tests.factories.fulfillment_factory import FulfillmentFactory
from dashboard.tests.factories.profile_factory import ProfileFactory


@pytest.mark.django_db
class TestProfile:
    """Test Profile model."""

    def test_creation(self):
        """Test Profile returned by factory is valid."""
        profile = ProfileFactory()

        assert isinstance(profile, Profile)

    def test_get_sum_collected(self):
        profile = ProfileFactory()
        bounty = BountyFactory(
            accepted=True,
            current_bounty=True,
            value_in_usdt_now=3,
            network='mainnet'
        )
        bounty2 = BountyFactory(
            accepted=True,
            current_bounty=True,
            value_in_usdt_now=10,
            network='mainnet'
        )
        FulfillmentFactory(bounty=bounty, profile=profile, bounty_id=bounty.pk)
        FulfillmentFactory(bounty=bounty2, profile=profile, bounty_id=bounty2.pk)

        assert (bounty._val_usd_db + bounty2._val_usd_db) == profile.get_sum(sum_type='collected', currency='usd')

    def test_get_sum_funded(self):
        profile = ProfileFactory()

        bounty = BountyFactory(
            accepted=True,
            current_bounty=True,
            value_in_usdt_now=3,
            network='mainnet',
            bounty_owner_github_username=profile.handle
        )

        assert bounty._val_usd_db == profile.get_sum(sum_type='funded', currency='usd')

    def test_get_sum_orgs(self):
        profile = ProfileFactory()

        bounty = BountyFactory(
            accepted=True,
            current_bounty=True,
            value_in_usdt_now=3,
            network='mainnet',
            org=profile
        )

        assert bounty._val_usd_db == profile.get_sum(sum_type='org', currency='usd')
