from datetime import datetime, timedelta
from io import StringIO

from django.core.management import call_command

import pytest
from grants.management.commands.grant_collections_shuffle import grant_collection_age_score, grant_meta_data_score

from ...models.factories.grant_collection_factory import GrantCollectionFactory
from ...models.factories.grant_factory import GrantFactory


@pytest.mark.django_db
def test_grant_collections_shuffle_grant_meta_data_score():
    grant_1 = GrantFactory()
    grant_2 = GrantFactory()
    
    grant_1.twitter_verified = True
    grant_2.twitter_verified = True
    
    grant_1.github_project_url = 'https://github.com/gitcoinco/web'
    grant_2.github_project_url = 'https://github.com/gitcoinco/web'
    
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
