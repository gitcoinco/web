from datetime import datetime
from decimal import Decimal
from importlib import import_module
from unittest import TestCase

import pytest
import pytest_django
from dashboard.models import Activity, Profile
from grants.models import Grant, Subscription
from pytz import UTC

grants = import_module('dashboard.migrations.0034_data_for_old_grants')


@pytest.fixture(autouse=True)
def start():
    pytest_django.plugin._blocking_manager.unblock()
    Grant.objects.all().delete()
    Subscription.objects.all().delete()
    Activity.objects.all().delete()
    yield
    Profile.objects.all().delete()

def test_close_enough():
    base_date = datetime(2019, 5, 27, 11, 6, 45, tzinfo=UTC)
    near_date = datetime(2019, 5, 27, 18, 33, 21, tzinfo=UTC)
    almost_one_exact_day_later = datetime(2019, 5, 28, 11, 6, 44, tzinfo=UTC)
    one_exact_day_later = datetime(2019, 5, 28, 11, 6, 45, tzinfo=UTC)
    far_date = datetime(2019, 5, 30, 19, 23, 51, tzinfo=UTC)
    assert grants.close_enough(base_date, near_date)
    assert grants.close_enough(near_date, base_date)
    assert grants.close_enough(base_date, almost_one_exact_day_later)
    assert grants.close_enough(almost_one_exact_day_later, base_date)
    assert not(grants.close_enough(base_date, one_exact_day_later))
    assert not(grants.close_enough(one_exact_day_later, base_date))
    assert not(grants.close_enough(base_date, far_date))
    assert not(grants.close_enough(far_date, base_date))

@pytest.fixture
def profile():
    profile, created = Profile.objects.get_or_create(
            data={},
            handle='e18r',
            email='e18r@localhost'
        )
    return profile

@pytest.fixture
def new_grant(profile):
    kwargs = {
        'created_on': datetime(2018, 12, 25, 14, 22, 35, tzinfo=UTC),
        'modified_on': datetime(2018, 12, 25, 14, 22, 55, tzinfo=UTC),
        'title': 'test 3',
        'description': 'test description',
        'reference_url': 'http://www.example.com',
        'admin_address': '0x8B04e71007A783B4965BaFE068EC062D935E93b5',
        'contract_owner_address': '0x8B04e71007A783B4965BaFE068EC062D935E93b5',
        'token_address': '0xFc1079D41D56D78e9FA2a857991F41D777104c74',
        'token_symbol': 'E18R',
        'amount_goal': Decimal('100.0000'),
        'contract_version':  Decimal('0'),
        'deploy_tx_id': '0xa95d30415427f76c778207e789c78d436b5c4ca4339797cff52ed21de8419554',
        'network': 'rinkeby',
        'metadata': {},
        'admin_profile': profile,
        'logo': None,
    }
    grant = Grant(**kwargs)
    grant.save(update=False)
    return grant

@pytest.fixture
def new_modern_grant(new_grant):
    new_grant.created_on = datetime(2019, 5, 27, 14, 12, 35, tzinfo=UTC)
    new_grant.modified_on = datetime(2019, 5, 27, 14, 12, 55, tzinfo=UTC)
    new_grant.save(update=False)
    return new_grant

@pytest.fixture
def new_grant_with_activity(new_grant, profile):
    kwargs = {
        'created_on': datetime(2018, 12, 25, 14, 22, 35, tzinfo=UTC),
        'profile': profile,
        'grant': new_grant,
        'activity_type': 'new_grant',
    }
    activity = Activity(**kwargs)
    activity.save(update=False)
    return new_grant

@pytest.fixture
def updated_grant(new_grant):
    new_grant.modified_on = datetime(2018, 12, 28, 14, 22, 35, tzinfo=UTC)
    new_grant.save(update=False)
    return new_grant

@pytest.fixture
def updated_grant_with_activity(updated_grant, profile):
    kwargs = {
        'created_on': datetime(2018, 12, 28, 14, 22, 35, tzinfo=UTC),
        'profile': profile,
        'grant': updated_grant,
        'activity_type': 'update_grant',
    }
    activity = Activity(**kwargs)
    activity.save(update=False)
    return updated_grant

@pytest.fixture
def killed_grant(updated_grant):
    updated_grant.active = False
    updated_grant.save(update=False)
    return updated_grant

@pytest.fixture
def killed_grant_with_activity(killed_grant, profile):
    kwargs = {
        'created_on': datetime(2018, 12, 28, 14, 22, 35, tzinfo=UTC),
        'profile': profile,
        'grant': killed_grant,
        'activity_type': 'killed_grant',
    }
    activity = Activity(**kwargs)
    activity.save(update=False)
    return killed_grant

@pytest.fixture
def new_subscription(new_grant, profile):
    kwargs = {
        'created_on': datetime(2018, 12, 29, 14, 22, 35, tzinfo=UTC),
        'active': False,
        'contributor_address': '0x8B04e71007A783B4965BaFE068EC062D935E93b5',
        'amount_per_period': 5,
        'real_period_seconds': 2592000,
        'frequency': 30,
        'frequency_unit': 'days',
        'token_address': '0xFc1079D41D56D78e9FA2a857991F41D777104c74',
        'token_symbol': 'E18R',
        'gas_price': 10,
        'new_approve_tx_id': '0xa95d30415427f76c778207e789c78d436b5c4ca4339797cff52ed21de8419554',
        'num_tx_approved': 12,
        'network': 'rinkeby',
        'contributor_profile': profile,
        'grant': new_grant,
        'last_contribution_date': datetime(2018, 1, 1, 15, 5, 25, tzinfo=UTC),
        'next_contribution_date': datetime(2020, 1, 1, 15, 5, 25, tzinfo=UTC),
    }
    return Subscription.objects.create(**kwargs)

@pytest.fixture
def new_subscription_with_activity(new_subscription, profile):
    kwargs = {
        'created_on': datetime(2018, 12, 29, 14, 22, 35, tzinfo=UTC),
        'profile': profile,
        'subscription': new_subscription,
        'activity_type': 'new_grant_subscription',
    }
    activity = Activity(**kwargs)
    activity.save(update=False)
    return new_subscription

@pytest.fixture
def new_contribution(new_subscription):
    contribution = new_subscription
    contribution.num_tx_approved = 1
    contribution.successful_contribution(contribution.new_approve_tx_id)
    contribution.error = True
    contribution.subminer_comments = "skipping"
    contribution.save()
    return contribution

@pytest.fixture
def new_contribution_with_activity(new_contribution, profile):
    kwargs = {
        'created_on': datetime(2018, 12, 29, 14, 22, 35, tzinfo=UTC),
        'profile': profile,
        'subscription': new_contribution,
        'activity_type': 'new_grant_contribution',
    }
    activity = Activity(**kwargs)
    activity.save(update=False)
    return new_contribution

@pytest.fixture
def cancelled_subscription(new_subscription):
    new_subscription.end_approve_tx_id = '0xa95d30415427f76c778207e789c78d436b5c4ca4339797cff52ed21de8419554'
    new_subscription.cancel_tx_id = '0xa95d30415427f76c778207e789c78d436b5c4ca4339797cff52ed21de8419554'
    new_subscription.active = False
    new_subscription.modified_on = datetime(2018, 12, 31, 14, 22, 35, tzinfo=UTC)
    new_subscription.save(update=False)
    return new_subscription

@pytest.fixture
def cancelled_subscription_with_activity(cancelled_subscription, profile):
    kwargs = {
        'created_on': datetime(2018, 12, 31, 14, 22, 35, tzinfo=UTC),
        'profile': profile,
        'subscription': cancelled_subscription,
        'activity_type': 'killed_grant_contribution',
    }
    activity = Activity(**kwargs)
    activity.save(update=False)
    return cancelled_subscription
    
def test_new_grant(new_grant):
    activities = Activity.objects.filter(grant = new_grant)
    assert len(activities) == 0
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(grant = new_grant)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'new_grant'
    assert activity.created_on == new_grant.created_on
    assert activity.profile == new_grant.admin_profile

def test_update_grant(updated_grant):
    activities = Activity.objects.filter(grant = updated_grant)
    assert len(activities) == 0
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(grant = updated_grant)
    assert len(activities) == 2
    assert 'update_grant' in [a.activity_type for a in activities]

def test_killed_grant(killed_grant):
    activities = Activity.objects.filter(grant = killed_grant)
    assert len(activities) == 0
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(grant = killed_grant)
    assert len(activities) == 2 # impossible to know if/when a killed grant was updated
    assert 'killed_grant' in [a.activity_type for a in activities]

def test_new_contribution(new_contribution):
    activities = Activity.objects.filter(subscription = new_contribution)
    assert len(activities) == 0
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(subscription = new_contribution)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'new_grant_contribution'
    assert activity.created_on == new_contribution.created_on
    assert activity.profile == new_contribution.contributor_profile

def test_new_subscription(new_subscription):
    activities = Activity.objects.filter(subscription = new_subscription)
    assert len(activities) == 0
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(subscription = new_subscription)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'new_grant_subscription'

def test_cancelled_subscription(cancelled_subscription):
    activities = Activity.objects.filter(subscription = cancelled_subscription)
    assert len(activities) == 0
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(subscription = cancelled_subscription)
    assert len(activities) == 2
    assert 'killed_grant_contribution' in [a.activity_type for a in activities]

def test_avoid_duplicate_new_grant_activity(new_grant_with_activity):
    activities = Activity.objects.filter(grant = new_grant_with_activity)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'new_grant'
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(grant = new_grant_with_activity)
    assert len(activities) == 1

def test_avoid_duplicate_updated_grant_activity(updated_grant_with_activity):
    activities = Activity.objects.filter(grant = updated_grant_with_activity)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'update_grant'
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(grant = updated_grant_with_activity)
    assert len([a for a in activities if a.activity_type == 'update_grant']) == 1

def test_avoid_duplicate_killed_grant_activity(killed_grant_with_activity):
    activities = Activity.objects.filter(grant = killed_grant_with_activity)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'killed_grant'
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(grant = killed_grant_with_activity)
    assert len([a for a in activities if a.activity_type == 'killed_grant']) == 1

def test_avoid_duplicate_new_subscription_activity(new_subscription_with_activity):
    activities = Activity.objects.filter(
        subscription = new_subscription_with_activity)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'new_grant_subscription'
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(subscription = new_subscription_with_activity)
    assert len(activities) == 1

def test_avoid_duplicate_new_contribution_activity(new_contribution_with_activity):
    activities = Activity.objects.filter(
        subscription = new_contribution_with_activity)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'new_grant_contribution'
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(subscription = new_contribution_with_activity)
    assert len(activities) == 1

def test_avoid_duplicate_cancelled_subscription_activity(cancelled_subscription_with_activity):
    activities = Activity.objects.filter(
        subscription = cancelled_subscription_with_activity)
    assert len(activities) == 1
    activity = activities[0]
    assert activity.activity_type == 'killed_grant_contribution'
    grants.generate_activities(None, None)
    activities = Activity.objects.filter(subscription = cancelled_subscription_with_activity)
    assert len([a for a in activities if a.activity_type == 'killed_grant_contribution']) == 1

def test_avoid_modern_grant_activity(new_modern_grant):
    activities = Activity.objects.filter(grant = new_modern_grant)
    assert len(activities) == 0
    grants.generate_activities(None, None)
    assert len(activities) == 0
