import pytest
from grants.tests.factories.grant_hall_of_fame_factory import GrantHallOfFameFactory, GrantHallOfFameGranteeFactory
from grants.models.hall_of_fame import GrantHallOfFame, GrantHallOfFameGrantee


@pytest.mark.django_db
class TestGrantHallOfFame:
    """Test GrantHallOfFame model."""

    def test_creation(self):
        """Test GrantHallOfFame data returned by factory is valid."""

        grant_hall_of_fame = GrantHallOfFameFactory()
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()
        

        assert isinstance(grant_hall_of_fame, GrantHallOfFame)
        assert isinstance(grant_hall_of_fame_grantee, GrantHallOfFameGrantee)

    def test_grant_hall_of_fame_has_total_donations(self):
        grant_hall_of_fame = GrantHallOfFameFactory()

        assert hasattr(grant_hall_of_fame, 'total_donations')

    def test_grant_hall_of_fame_has_top_matching_partners(self):
        grant_hall_of_fame = GrantHallOfFameFactory()

        assert hasattr(grant_hall_of_fame, 'top_matching_partners')

    def test_grant_hall_of_fame_has_top_matching_partners_mobile_attribute(self):
        grant_hall_of_fame = GrantHallOfFameFactory()

        assert hasattr(grant_hall_of_fame, 'top_matching_partners_mobile')

    def test_grant_hall_of_fame_has_top_individual_donors(self):
        grant_hall_of_fame = GrantHallOfFameFactory()

        assert hasattr(grant_hall_of_fame, 'top_individual_donors')

    def test_grant_hall_of_fame_has_top_individual_donors_mobile(self):
        grant_hall_of_fame = GrantHallOfFameFactory()

        assert hasattr(grant_hall_of_fame, 'top_individual_donors_mobile')

    def test_grant_hall_of_fame_has_graduated_grantees_description(self):
        grant_hall_of_fame = GrantHallOfFameFactory()

        assert hasattr(grant_hall_of_fame, 'graduated_grantees_description')

    def test_grant_hall_of_fame_has_share_your_story_email(self):
        grant_hall_of_fame = GrantHallOfFameFactory()

        assert hasattr(grant_hall_of_fame, 'share_your_story_email')

    def test_grant_has_is_published_attribute(self):
        grant_hall_of_fame = GrantHallOfFameFactory()

        assert hasattr(grant_hall_of_fame, 'is_published')
        assert grant_hall_of_fame.is_published == False

    def test_grant_hall_of_fame_grantee_has_associated_hall_of_fame(self):
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()

        assert hasattr(grant_hall_of_fame_grantee, 'hall_of_fame')

    def test_grant_hall_of_fame_grantee_has_grantee(self):
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()

        assert hasattr(grant_hall_of_fame_grantee, 'grantee')

    def test_grant_hall_of_fame_grantee_has_a_name(self):
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()

        assert hasattr(grant_hall_of_fame_grantee, 'name')

    def test_grant_hall_of_fame_grantee_has_funded_by_attribute(self):
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()

        assert hasattr(grant_hall_of_fame_grantee, 'funded_by')

    def test_grant_hall_of_fame_grantee_has_an_amount(self):
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()

        assert hasattr(grant_hall_of_fame_grantee, 'amount')

    def test_grant_hall_of_fame_grantee_has_a_description(self):
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()

        assert hasattr(grant_hall_of_fame_grantee, 'description')

    def test_grant_hall_of_fame_grantee_has_accomplishment_1(self):
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()

        assert hasattr(grant_hall_of_fame_grantee, 'accomplishment_1')

    def test_grant_hall_of_fame_grantee_has_accomplishment_2(self):
        grant_hall_of_fame_grantee = GrantHallOfFameGranteeFactory()

        assert hasattr(grant_hall_of_fame_grantee, 'accomplishment_2')
    
    