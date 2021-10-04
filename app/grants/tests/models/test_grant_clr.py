from unittest.mock import patch

from django.utils import timezone

import pytest
from dashboard.models import Profile
from grants.models.grant import Grant, GrantCLR
from grants.models.grant_clr_calculation import GrantCLRCalculation
from grants.models.grant_collection import GrantCollection

from .factories.grant_clr_factory import GrantCLRFactory
from .factories.grant_collection_factory import GrantCollectionFactory
from .factories.grant_factory import GrantFactory


@pytest.mark.django_db
class TestGrantCLR:
    """Test GrantCLR model."""

    def test_creation(self):
        """Test GrantCLR returned by factory is valid."""

        grant_clr = GrantCLRFactory()

        assert isinstance(grant_clr, GrantCLR)

    def test_grant_clr_has_a_customer_name(self):
        """Test customer_name attribute is present and defaults to empty string."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'customer_name')
        assert grant_clr.customer_name == ''

    def test_grant_clr_has_round_num_attribute(self):
        """Test round_num attribute is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'round_num')
    
    def test_grant_clr_has_sub_round_slug_attribute(self):
        """Test sub_round_slug attribute is present and defaults to empty string."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'sub_round_slug')
        assert grant_clr.sub_round_slug == ''

    def test_grant_clr_has_display_text_attribute(self):
        """Test display_text attribute is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'display_text')

    def test_grant_clr_has_owner_attribute(self):
        """Test owner attribute is present and is an instance of Profile."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'owner')
        assert isinstance(grant_clr.owner, Profile)

    def test_grant_clr_has_is_active_attribute(self):
        """Test is_active attribute is present and defaults to False."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'is_active')
        assert grant_clr.is_active == False

    def test_grant_clr_has_start_date_attribute(self):
        """Test start_date is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'start_date')

    def test_grant_clr_has_end_date_attribute(self):
        """Test end_date is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'end_date')

    def test_grant_clr_has_grant_filters(self):
        """Test grant_filters attribute is present and defaults to an empty dictionary."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'grant_filters')
        assert grant_clr.grant_filters == {}
        assert len(grant_clr.grant_filters) == 0

    def test_grant_clr_has_subscription_filters(self):
        """Test subscription_filters attribute is present and defaults to an empty dictionary."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'subscription_filters')
        assert grant_clr.subscription_filters == {}
        assert len(grant_clr.subscription_filters) == 0

    def test_grant_clr_has_collection_filters(self):
        """Test collection_filters attribute is present and defaults to an empty dictionary."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'collection_filters')
        assert grant_clr.collection_filters == {}
        assert len(grant_clr.collection_filters) == 0

    def test_grant_clr_has_verified_threshold(self):
        """Test verified_threshold is present and defaults to 25.0."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'verified_threshold')
        assert grant_clr.verified_threshold == 25.0

    def test_grant_clr_has_unverified_threshold(self):
        """Test unverified_threshold is present and defaults to 5.0."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'unverified_threshold')
        assert grant_clr.unverified_threshold == 5.0

    def test_grant_clr_has_total_pot(self):
        """Test total_pot is present and defaults to 0."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'total_pot')
        assert grant_clr.total_pot == 0

    def test_grant_clr_contribution_multiplier(self):
        """Test contribution_multiplier is present and defaults to 1.0."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'contribution_multiplier')
        assert grant_clr.contribution_multiplier == 1.0

    def test_grant_clr_has_logo_attribute(self):
        """Test logo attribute is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'logo')

    def test_happening_now_returns_true_if_round_is_currently_happening(self):
        """Test happening_now method returns true if we are within the time range for this round."""

        grant_clr = GrantCLRFactory()
        grant_clr.start_date = timezone.now() - timezone.timedelta(days=3)
        grant_clr.end_date = timezone.now() + timezone.timedelta(days=4)

        assert grant_clr.happening_now == True

    def test_happening_now_returns_false_if_round_is_not_currently_happening(self):
        """Test happening_now method returns false if we are outside the time range for this round."""

        grant_clr = GrantCLRFactory()
        grant_clr.start_date = timezone.now() + timezone.timedelta(days=3)
        grant_clr.end_date = timezone.now() + timezone.timedelta(days=10)

        assert grant_clr.happening_now == False

    def test_happened_recently_returns_true_if_round_happened_recently(self):
        """Test happened_recently method returns true if grant_clr.end_date is within two weeks of current round."""

        grant_clr = GrantCLRFactory()
        grant_clr.start_date = timezone.now()
        grant_clr.end_date = timezone.now() - timezone.timedelta(days=10)

        assert grant_clr.happened_recently == True

    def test_happened_recently_returns_false_if_round_did_not_happen_recently(self):
        """Test happened_recently method returns false if grant_clr.end_date is not within two weeks of current round."""

        grant_clr = GrantCLRFactory()
        grant_clr.start_date = timezone.now()
        grant_clr.end_date = timezone.now() - timezone.timedelta(days=20)

        assert grant_clr.happened_recently == False

    def test_grants_method_calls_filter_with_expected_parameters(self):
        grant_clr = GrantCLRFactory()

        with patch.object(Grant.objects, 'filter') as filter:
            grant_clr.grants

        filter.assert_called_with(
            hidden=False,
            active=True,
            is_clr_eligible=True,
            link_to_new_grant=None
        )

    def test_grants_method_calls_filter_with_expected_parameters_if_collection_filters_are_present(self):
        grant_clr = GrantCLRFactory()
        grant_clr.collection_filters={'1': GrantCollectionFactory()}
        grants = Grant.objects.filter(hidden=False, active=True, is_clr_eligible=True, link_to_new_grant=None)

        with patch.object(GrantCollection.objects, 'filter') as filter:
            with patch.object(GrantCollection.objects.filter(**grant_clr.collection_filters), 'values_list') as values_list:
                grant_clr.grants

        filter.assert_called_with(**grant_clr.collection_filters)
        values_list.assert_called_with('grants', flat=True)

    def test_grants_method_does_not_call_filter_if_collection_filters_are_not_present(self):
        grant_clr = GrantCLRFactory()

        with patch.object(GrantCollection.objects, 'filter') as filter:
            with patch.object(GrantCollection.objects.filter(**grant_clr.collection_filters), 'values_list') as values_list:
                grant_clr.grants

        filter.assert_not_called
        values_list.assert_not_called 

    def test_record_clr_prediction_curve_calls_collaborator_with_expected_parameters(self):
        """Test record_clr_prediction_curve calls create on GrantCLRCalculation.objects with expected params."""

        grant = GrantFactory()
        grant_clr = GrantCLRFactory()
        
        with patch.object(GrantCLRCalculation.objects, 'create') as create:
            grant_clr.record_clr_prediction_curve(grant, grant.clr_prediction_curve)

        create.assert_called_with(
            grantclr=grant_clr, 
            grant=grant, 
            clr_prediction_curve=grant.clr_prediction_curve,
            latest=True
        )

    def test_grant_clr_has_claim_start_date_attribute(self):
        """Test claim_start_date is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'claim_start_date')

    def test_grant_clr_has_claim_end_date_attribute(self):
        """Test claim_end_date is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'claim_end_date')
