import pytest
from dashboard.models import Profile
from grants.models.grant import Grant, GrantCLR
from grants.models.grant_category import GrantCategory
from grants.models.grant_type import GrantType

from .factories.grant_category_factory import GrantCategoryFactory
from .factories.grant_clr_factory import GrantCLRFactory
from .factories.grant_factory import GrantFactory
from .factories.profile_factory import ProfileFactory


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

    def test_grant_has_contract_address_attribute(self):
        """Test contract_address attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'contract_address')
        assert grant.contract_address == '0x0'

    def test_grant_has_deploy_tx_id(self):
        """Test deploy_tx_id attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'deploy_tx_id')
        assert grant.deploy_tx_id == '0x0'

    def test_grant_has_cancel_tx_id(self):
        """Test cancel_tx_id attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'cancel_tx_id')
        assert grant.cancel_tx_id == '0x0'

    def test_grant_has_a_contract_version(self):
        """Test contract_version attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'contract_version')
        assert grant.contract_version == 0

    def test_grant_has_metadata(self):
        """Test metadata attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'metadata')
        assert grant.metadata == {}
        assert len(grant.metadata) == 0

    def test_grant_has_network_attribute(self):
        """Test network attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'network')
        assert grant.network == 'mainnet'

    def test_grant_has_required_gas_price(self):
        """Test required_gas_price attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'required_gas_price')
        assert grant.required_gas_price == '0'

    def test_grant_has_admin_profile(self):
        """Test admin_profile attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'admin_profile')
        assert grant.admin_profile == None

    def test_grant_has_team_members(self):
        """Test team_members attribute."""
        
        team_members = (ProfileFactory(), ProfileFactory(handle='gitcoinbot2'))
        grant = GrantFactory(team_members=(team_members))

        assert hasattr(grant, 'team_members')
        assert len(grant.team_members.all()) == len(team_members)
        assert isinstance(grant.team_members.first(), Profile)

    def test_grant_has_image_css(self):
        """Test image_css attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'image_css')
        assert grant.image_css == ''

    def test_grant_has_amount_received_with_phantom_funds(self):
        """Test amount_received_with_phantom_funds attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'amount_received_with_phantom_funds')
        assert grant.amount_received_with_phantom_funds == 0

    def test_grant_has_active_subscriptions(self):
        """Test activeSubscriptions attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'activeSubscriptions')
        assert grant.activeSubscriptions == []

    def test_grant_has_hidden_attribute(self):
        """Test 'hidden' attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'hidden')
        assert grant.hidden == False

    def test_grant_has_random_shuffle_attribute(self):
        """Test random_shuffle attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'random_shuffle')
        assert grant.random_shuffle == None

    def test_grant_has_weighted_shuffle_attribute(self):
        """Test weighted_shuffle attribute is present and blank."""

        grant = GrantFactory()

        assert hasattr(grant, 'weighted_shuffle')
        assert grant.weighted_shuffle == None

    def test_grant_has_contribution_count(self):
        """Test contribution_count_attribute and defaults to 0."""

        grant = GrantFactory()

        assert hasattr(grant, 'contribution_count')
        assert grant.contribution_count == 0

    def test_grant_has_contributor_count(self):
        """Test contributor_count attribute is present and defaults to 0."""

        grant = GrantFactory()

        assert hasattr(grant, 'contributor_count')
        assert grant.contributor_count == 0

    def test_grant_has_positive_round_contributor_count(self):
        """Test positive_round_contributor_count is present and defaults to 0."""

        grant = GrantFactory()

        assert hasattr(grant, 'positive_round_contributor_count')
        assert grant.positive_round_contributor_count == 0

    def test_grant_has_negative_round_contributor_count(self):
        """Test negative_round_contributor_count is present and defaults to 0."""

        grant = GrantFactory()

        assert hasattr(grant, 'negative_round_contributor_count')
        assert grant.negative_round_contributor_count == 0

    def test_grant_has_defer_clr_to_attribute(self):
        """Test defer_clr_to attribute is present and blank."""

        grant = GrantFactory()

        assert hasattr(grant, 'defer_clr_to')
        assert grant.defer_clr_to == None

    def test_grant_has_last_clr_calc_date_attribute(self):
        """Test last_clr_calc_date attribute is present and blank."""

        grant = GrantFactory()

        assert hasattr(grant, 'last_clr_calc_date')
        assert grant.last_clr_calc_date == None

    def test_grant_has_next_clr_calc_date_attribute(self):
        """Test next_clr_calc_date attribute is present and blank."""

        grant = GrantFactory()

        assert hasattr(grant, 'next_clr_calc_date')
        assert grant.next_clr_calc_date == None

    def test_grant_has_last_update_attribute(self):
        """Test last_update attribute is present and blank."""

        grant = GrantFactory()

        assert hasattr(grant, 'last_update')
        assert grant.last_update == None

    def test_grant_has_categories(self):
        """Test categories attribute is present and blank."""
        
        categories = (GrantCategoryFactory(), GrantCategoryFactory())
        grant = GrantFactory(categories=(categories))

        assert hasattr(grant, 'categories')
        assert isinstance(grant.categories.first(), GrantCategory)
        assert len(grant.categories.all()) == 2

    def test_grant_has_twitter_handle_1(self):
        """Test twitter_handle_1 attribute is present and defaults to empty string."""

        grant = GrantFactory()

        assert hasattr(grant, 'twitter_handle_1')
        assert grant.twitter_handle_1 == ''

    def test_grant_has_twitter_handle_2(self):
        """Test twitter_handle_2 attribute is present and defaults to empty string."""

        grant = GrantFactory()

        assert hasattr(grant, 'twitter_handle_2')
        assert grant.twitter_handle_2 == ''

    def test_grant_has_twitter_handle_1_follower_count(self):
        """Test twitter_handle_1_follower_count is present and defaults to 0."""

        grant = GrantFactory()

        assert hasattr(grant, 'twitter_handle_1_follower_count')
        assert grant.twitter_handle_1_follower_count == 0

    def test_grant_has_twitter_handle_2_follower_count(self):
        """Test twitter_handle_2_follower_count is present and defaults to 0."""

        grant = GrantFactory()

        assert hasattr(grant, 'twitter_handle_2_follower_count')
        assert grant.twitter_handle_2_follower_count == 0

    def test_grant_has_sybil_score(self):
        """Test sybil_score attribute is present and defaults to 0."""

        grant = GrantFactory()

        assert hasattr(grant, 'sybil_score')
        assert grant.sybil_score == 0

    def test_grant_has_funding_info(self):
        """Test funding_info attribute is present and defaults to empty string."""

        grant = GrantFactory()

        assert hasattr(grant, 'funding_info')
        assert grant.funding_info == ''

    def test_grant_has_has_external_funding_attribute(self):
        """Test has_external_funding attribute is present and defaults to 'unknown'."""

        grant = GrantFactory()

        assert hasattr(grant, 'has_external_funding')
        assert grant.has_external_funding == 'unknown'

    def test_grant_has_clr_prediction_curve_attribute(self):
        """Test clr_prediction_curve attribute is present."""

        grant = GrantFactory()

        assert hasattr(grant, 'clr_prediction_curve')
        assert len(grant.clr_prediction_curve) == 6

    def test_grant_has_weighted_risk_score(self):
        """Test weighted_risk_score attribute is present and defaults to 0."""

        grant = GrantFactory()

        assert hasattr(grant, 'weighted_risk_score')
        assert grant.weighted_risk_score == 0

    def test_grant_has_in_active_clrs_attribute(self):
        """Test in_active_clrs_attribute is present."""
        
        grant_clrs = (GrantCLRFactory(), GrantCLRFactory(round_num=4))
        grant = GrantFactory(in_active_clrs=(grant_clrs))

        assert hasattr(grant, 'in_active_clrs')
        assert isinstance(grant.in_active_clrs.first(), GrantCLR)
