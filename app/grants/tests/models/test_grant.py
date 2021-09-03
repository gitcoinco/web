import pytest
from grants.models.grant import Grant
from grants.models.grant_type import GrantType

from .factories.grant_factory import GrantFactory


@pytest.mark.django_db
class TestGrant:
    """Test Grant model."""

    def test_creation(self):
        """Test instance of Grant returned by factory is valid."""

        grant = GrantFactory()

        assert isinstance(grant, Grant)

    def test_grant_has_vector_column(self):
        """Test vector_column attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'vector_column')
        assert grant.vector_column == None

    def test_grant_has_active_attribute(self):
        """Test active attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'active')
        assert grant.active == True

    def test_grant_has_associated_grant_type(self):
        """Test association with GrantType."""

        grant = GrantFactory()

        assert hasattr(grant, 'grant_type')
        assert isinstance(grant.grant_type, GrantType)

    def test_grant_has_a_title(self):
        """Test title attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'title')
        assert grant.title == ''

    def test_grant_has_a_slug(self):
        """Test slug attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'slug')
    
    def test_grant_has_a_description(self):
        """Test description attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'description')
        assert grant.description == ''

    def test_grant_has_description_rich_attribute(self):
        """Test description_rich attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'description_rich')
        assert grant.description_rich == ''

    def test_grant_has_reference_url(self):
        """Test reference_url attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'reference_url')
        assert grant.reference_url == ''

    def test_grant_has_github_project_url(self):
        """Test github_project_url attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'github_project_url')
        assert grant.github_project_url == None

    def test_grant_has_is_clr_eligible_attribute(self):
        """Test is_clr_eligible attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'is_clr_eligible')
        assert grant.is_clr_eligible == True

    def test_grant_has_admin_message_attribute(self):
        """Test admin_message attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'admin_message')
        assert grant.admin_message == ''

    def test_grant_has_visible_attribute(self):
        """Test visible attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'visible')
        assert grant.visible == True

    def test_grant_has_region_attribute(self):
        """Test region attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'region')
        assert grant.region == None

    def test_grant_has_link_to_new_grant_attribute(self):
        """Test link_to_new_grant attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'link_to_new_grant')
        assert grant.link_to_new_grant == None

    def test_grant_has_a_logo_attribute(self):
        """Test logo attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'logo')
        assert grant.logo == None

    def test_grant_has_a_logo_svg_attribute(self):
        """Test logo_svg attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'logo_svg')
        assert grant.logo_svg == None

    def test_grant_has_admin_address_attribute(self):
        """Test admin_address attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'admin_address')
        assert grant.admin_address == '0x0'

    def test_grant_has_zcash_payout_address_attribute(self):
        """Test zcash_payout_address_attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'zcash_payout_address')
        assert grant.zcash_payout_address == '0x0'

    def test_grant_has_celo_payout_address(self):
        """Test celo_payout_address_and_default."""

        grant = GrantFactory()

        assert hasattr(grant, 'celo_payout_address')
        assert grant.celo_payout_address == '0x0'

    def test_grant_has_zil_payout_address(self):
        """Test zil_payout_address_and_default."""

        grant = GrantFactory()

        assert hasattr(grant, 'zil_payout_address')
        assert grant.zil_payout_address == '0x0'

    def test_grant_has_polkadot_payout_address(self):
        """Test polkadot_payout_address_and_default."""

        grant = GrantFactory()

        assert hasattr(grant, 'polkadot_payout_address')
        assert grant.polkadot_payout_address == '0x0'

    def test_grant_has_kusama_payout_address(self):
        """Test kusama_payout_address_and_default."""

        grant = GrantFactory()

        assert hasattr(grant, 'kusama_payout_address')
        assert grant.kusama_payout_address == '0x0'

    def test_grant_has_harmony_payout_address(self):
        """Test harmony_payout_address_and_default."""

        grant = GrantFactory()

        assert hasattr(grant, 'harmony_payout_address')
        assert grant.harmony_payout_address == '0x0'

    def test_grant_has_binance_payout_address(self):
        """Test binance_payout_address_and_default."""

        grant = GrantFactory()

        assert hasattr(grant, 'binance_payout_address')
        assert grant.binance_payout_address == '0x0'

    def test_grant_has_rsk_payout_address(self):
        """Test rsk_payout_address_and_default."""

        grant = GrantFactory()

        assert hasattr(grant, 'rsk_payout_address')
        assert grant.rsk_payout_address == '0x0'

    def test_grant_has_algorand_payout_address(self):
        """Test algorand_payout_address_and_default."""

        grant = GrantFactory()

        assert hasattr(grant, 'algorand_payout_address')
        assert grant.algorand_payout_address == '0x0'
        
    def test_grant_has_contract_owner_address(self):
        """Test contract_owner_address attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'contract_owner_address')
        assert grant.contract_owner_address == '0x0'

    def test_grant_has_amount_received_in_round_attribute(self):
        """Test amount_received_in_round attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'amount_received_in_round')
        assert grant.amount_received_in_round == 0

    def test_grant_has_monthly_amount_subscribed_attribute(self):
        """Test monthly_amount_subscribed_attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'monthly_amount_subscribed')
        assert grant.monthly_amount_subscribed == 0

    def test_grant_has_amount_received_attribute(self):
        """Test amount_received attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'amount_received')
        assert grant.amount_received == 0

    def test_grant_has_token_address_attribute(self):
        """Test token_address attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'token_address')
        assert grant.token_address == '0x0'

    def test_grant_has_token_symbol_attribute(self):
        """Test token_symbol attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'token_symbol')
        assert grant.token_symbol == ''

    


    
    

    