import pytest

from dashboard.tests.factories import BountyFactory


@pytest.fixture()
def bounty(db):
    return BountyFactory()


@pytest.mark.django_db
class TestBountyDBAttributes:
    """Assertions against the db backed fields of the Bounty class"""
    def test_bounty_state(self, bounty):
        assert hasattr(bounty, 'bounty_state')
        assert bounty.bounty_state == 'open'

    def test_web3_type(self, bounty):
        assert hasattr(bounty, 'web3_type')
        assert bounty.web3_type == 'bounties_network'

    def test_title(self, bounty):
        assert hasattr(bounty, 'title')
        assert bounty.title == ''

    def test_web3_created(self, bounty):
        assert hasattr(bounty, 'web3_created')
        assert bounty.web3_created is not None

    def test_value_in_token(self, bounty):
        assert hasattr(bounty, 'value_in_token')
        assert bounty.value_in_token == 1.00

    def test_token_name(self, bounty):
        assert hasattr(bounty, 'token_name')
        assert bounty.token_name == ''

    def test_token_address(self, bounty):
        assert hasattr(bounty, 'token_address')
        assert bounty.token_address == ''

    def test_bounty_type(self, bounty):
        assert hasattr(bounty, 'bounty_type')
        assert bounty.bounty_type == ''

    def test_project_length(self, bounty):
        assert hasattr(bounty, 'project_length')
        assert bounty.project_length == ''
