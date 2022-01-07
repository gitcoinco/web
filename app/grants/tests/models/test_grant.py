import pytest
from grants.models.grant import Grant
from grants.models.grant_type import GrantType
from grants.tests.factories import GrantFactory


@pytest.mark.django_db
class TestGrant:
    """Test Grant model."""

    def test_creation(self):
        """Test instance of Grant returned by factory is valid."""

        grant = GrantFactory()

        assert isinstance(grant, Grant)

    def test_grant_has_vector_column(self):
        """Test Grant has vector_column attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'vector_column')

    def test_grant_has_active_attribute(self):
        """Test Grant has active attribute and that it defaults to true."""

        grant = GrantFactory()

        assert hasattr(grant, 'active')
        assert grant.active == True

    def test_grant_has_associated_grant_type(self):
        """Test Grant has associated GrantType."""

        grant = GrantFactory()

        assert hasattr(grant, 'grant_type')
        assert isinstance(grant.grant_type, GrantType)

    def test_grant_has_a_title(self):
        """Test Grant has a title attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'title')

    def test_grant_has_a_slug(self):
        """Test Grant has a slug attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'slug')

    def test_grant_has_a_description(self):
        """Test Grant has a description attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'description')

    def test_grant_has_a_description_rich_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'description_rich')
        assert grant.description_rich == ''

    def test_grant_has_a_reference_url(self):
        grant = GrantFactory()

        assert hasattr(grant, 'reference_url')

    def test_grant_has_a_github_project_url(self):
        grant = GrantFactory()

        assert hasattr(grant, 'github_project_url')

    def test_grant_has_is_clr_eligible_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'is_clr_eligible')
        assert grant.is_clr_eligible == True

    def test_grant_has_admin_message_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'admin_message')
        assert grant.admin_message == ''

    def test_grant_has_visible_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'visible')
        assert grant.visible == True

    def test_grant_has_region_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'region')

    def test_grant_has_link_to_new_grant(self):
        grant = GrantFactory()

        assert hasattr(grant, 'link_to_new_grant')

    def test_grant_has_a_logo(self):
        grant = GrantFactory()

        assert hasattr(grant, 'logo')

    def test_grant_has_a_logo_svg(self):
        grant = GrantFactory()

        assert hasattr(grant, 'logo_svg')

    def test_grant_has_admin_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'admin_address')

    def test_grant_has_zcash_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'zcash_payout_address')

    def test_grant_has_celo_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'celo_payout_address')

    def test_grant_has_zil_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'zil_payout_address')

    def test_grant_has_polkadot_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'polkadot_payout_address')

    def test_grant_has_kusama_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'kusama_payout_address')

    def test_grant_has_harmony_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'harmony_payout_address')

    def test_grant_has_binance_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'binance_payout_address')

    def test_grant_has_rsk_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'rsk_payout_address')

    def test_grant_has_algorand_payout_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'algorand_payout_address')

    def test_grant_has_contract_owner_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'contract_owner_address')

    