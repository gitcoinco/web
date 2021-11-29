from datetime import datetime, timedelta
from io import StringIO

from django.core.management import call_command

import pytest
from grants.management.commands.grant_collections_shuffle import grant_collection_age_score, grant_meta_data_score
from grants.tests.factories import GrantFactory


@pytest.mark.django_db
def test_grant_collections_shuffle_grant_meta_data_score():
    grant_1 = GrantFactory(twitter_verified=True, github_project_url='https://github.com/gitcoinco/web')
    grant_2 = GrantFactory(twitter_verified=True, github_project_url='https://github.com/gitcoinco/web')
    grants = (grant_1, grant_2)

    score = grant_meta_data_score(grants)

    assert score == 12000

@pytest.mark.django_db
def test_grant_collections_shuffle_calc_age_score():
    today = datetime.now()
    last_month = today - (today - timedelta(days=28))
    last_week = today - timedelta(days=7)

    score = grant_collection_age_score(last_month, last_week)

    assert score == 3750
