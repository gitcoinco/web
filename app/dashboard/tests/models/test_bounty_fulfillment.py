from attr import has
import pytest

from dashboard.models import BountyFulfillment
from dashboard.tests.factories.fulfillment_factory import FulfillmentFactory
from dashboard.tests.factories.bounty_factory import BountyFactory

@pytest.mark.django_db
class TestBountyFulfillmentProperties:
    def test_fulfillment_has_bounty(self):
        fulfillment = FulfillmentFactory()
        assert hasattr(fulfillment, 'bounty')

    def test_deleting_bounty_deletes_fulfillment(self):
        bounty = BountyFactory()
        fulfillment = FulfillmentFactory(bounty=bounty)

        bounty.delete()

        with pytest.raises(BountyFulfillment.DoesNotExist):
            fulfillment.refresh_from_db()
