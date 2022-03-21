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
        grant = GrantFactory()

        assert hasattr(grant, 'vector_column')

    def test_grant_has_active_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'active')
        assert grant.active == True

    def test_grant_has_associated_grant_type(self):
        grant = GrantFactory()

        assert hasattr(grant, 'grant_type')
        assert isinstance(grant.grant_type, GrantType)

    def test_grant_has_a_title(self):
        grant = GrantFactory()

        assert hasattr(grant, 'title')

    def test_grant_has_a_slug(self):
        grant = GrantFactory()

        assert hasattr(grant, 'slug')

    def test_grant_has_a_description(self):
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

    def test_grant_has_amount_received_in_round(self):
        grant = GrantFactory()

        assert hasattr(grant, 'amount_received_in_round')
        assert grant.amount_received_in_round == 0

    def test_grant_has_monthly_amount_subscribed(self):
        grant = GrantFactory()

        assert hasattr(grant, 'monthly_amount_subscribed')
        assert grant.monthly_amount_subscribed == 0

    def test_grant_has_amount_received(self):
        grant = GrantFactory()

        assert hasattr(grant, 'amount_received')
        assert grant.amount_received == 0

    def test_grant_has_a_token_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'token_address')
        assert grant.token_address == '0x0'

    def test_grant_has_a_token_symbol(self):
        grant = GrantFactory()

        assert hasattr(grant, 'token_symbol')
        assert grant.token_symbol == ''

    def test_grant_has_a_contract_address(self):
        grant = GrantFactory()

        assert hasattr(grant, 'contract_address')
        assert grant.contract_address == '0x0'

    def test_grant_has_deploy_tx_id(self):
        grant = GrantFactory()

        assert hasattr(grant, 'deploy_tx_id')
        assert grant.deploy_tx_id == '0x0'

    def test_grant_has_cancel_tx_id(self):
        grant = GrantFactory()

        assert hasattr(grant, 'cancel_tx_id')
        assert grant.cancel_tx_id == '0x0'

    def test_grant_has_contract_version(self):
        grant = GrantFactory()

        assert hasattr(grant, 'contract_version')
        assert grant.contract_version == 0

    def test_grant_has_metadata(self):
        grant = GrantFactory()

        assert hasattr(grant, 'metadata')
        assert grant.metadata == {}

    def test_grant_has_network(self):
        grant = GrantFactory()

        assert hasattr(grant, 'network')
        assert grant.network == 'mainnet'

    def test_grant_has_required_gas_price(self):
        grant = GrantFactory()

        assert hasattr(grant, 'required_gas_price')
        assert grant.required_gas_price == '0'

    def test_grant_has_admin_profile(self):
        grant = GrantFactory()

        assert hasattr(grant, 'admin_profile')

    def test_grant_has_team_members(self):
        grant = GrantFactory()

        assert hasattr(grant, 'team_members')

    def test_grant_has_image_css(self):
        grant = GrantFactory()

        assert hasattr(grant, 'image_css')
        assert grant.image_css == ''

    def test_grant_has_amount_received_with_phantom_funds(self):
        grant = GrantFactory()

        assert hasattr(grant, 'amount_received_with_phantom_funds')
        assert grant.amount_received_with_phantom_funds == 0

    def test_grant_has_active_subscriptions(self):
        grant = GrantFactory()

        assert hasattr(grant, 'activeSubscriptions')
        assert grant.activeSubscriptions == []

    def test_grant_has_hidden_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'hidden')
        assert grant.hidden == False

    def test_grant_has_random_shuffle(self):
        grant = GrantFactory()

        assert hasattr(grant, 'random_shuffle')

    def test_grant_has_weighted_shuffle(self):
        grant = GrantFactory()

        assert hasattr(grant, 'weighted_shuffle')

    def test_grant_has_contribution_count(self):
        grant = GrantFactory()

        assert hasattr(grant, 'contribution_count')
        assert grant.contribution_count == 0

    def test_grant_has_contributor_count(self):
        grant = GrantFactory()

        assert hasattr(grant, 'contributor_count')
        assert grant.contributor_count == 0

    def test_grant_has_positive_round_contributor_count(self):
        grant = GrantFactory()

        assert hasattr(grant, 'positive_round_contributor_count')
        assert grant.positive_round_contributor_count == 0

    def test_grant_has_negative_round_contributor_count(self):
        grant = GrantFactory()

        assert hasattr(grant, 'negative_round_contributor_count')
        assert grant.negative_round_contributor_count == 0

    def test_grant_has_defer_clr_to_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'defer_clr_to')

    def test_grant_has_last_clr_calc_date(self):
        grant = GrantFactory()

        assert hasattr(grant, 'last_clr_calc_date')

    def test_grant_has_last_update(self):
        grant = GrantFactory()

        assert hasattr(grant, 'last_update')

    def test_grant_has_categories(self):
        grant = GrantFactory()

        assert hasattr(grant, 'categories')

    def test_grant_has_tags(self):
        grant = GrantFactory()

        assert hasattr(grant, 'tags')

    def test_grant_has_twitter_handle_1(self):
        grant = GrantFactory()

        assert hasattr(grant, 'twitter_handle_1')
        assert grant.twitter_handle_1 == ''

    def test_grant_has_twitter_handle_2(self):
        grant = GrantFactory()

        assert hasattr(grant, 'twitter_handle_2')
        assert grant.twitter_handle_2 == ''

    def test_grant_has_twitter_handle_1_follower_count(self):
        grant = GrantFactory()

        assert hasattr(grant, 'twitter_handle_1_follower_count')
        assert grant.twitter_handle_1_follower_count == 0

    def test_grant_has_twitter_handle_2_follower_count(self):
        grant = GrantFactory()

        assert hasattr(grant, 'twitter_handle_2_follower_count')
        assert grant.twitter_handle_2_follower_count == 0

    def test_grant_has_sybil_score(self):
        grant = GrantFactory()

        assert hasattr(grant, 'sybil_score')
        assert grant.sybil_score == 0

    def test_grant_has_funding_info(self):
        grant = GrantFactory()

        assert hasattr(grant, 'funding_info')
        assert grant.funding_info == ''

    def test_grant_has_a_has_external_funding_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'has_external_funding')
        assert grant.has_external_funding == 'unknown'

    def test_grant_has_clr_prediction_curve(self):
        grant = GrantFactory()
        expected_curve = [
            [0.0, 0.0, 0.0], 
            [0.0, 0.0, 0.0], 
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0]
        ]

        assert hasattr(grant, 'clr_prediction_curve')
        assert grant.clr_prediction_curve == expected_curve

    def test_grant_has_weighted_risk_score(self):
        grant = GrantFactory()

        assert hasattr(grant, 'weighted_risk_score')
        assert grant.weighted_risk_score == 0

    def test_grant_has_an_in_active_clrs_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'in_active_clrs')

    def test_grant_has_is_clr_active_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'is_clr_active')
        assert grant.is_clr_active == False

    def test_grant_has_clr_round_num(self):
        grant = GrantFactory()

        assert hasattr(grant, 'clr_round_num')
        assert grant.clr_round_num == ''

    def test_grant_has_twitter_verified_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'twitter_verified')
        assert grant.twitter_verified == False

    def test_grant_has_twitter_verified_by_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'twitter_verified_by')

    def test_grant_has_twitter_verified_at_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'twitter_verified_at')
