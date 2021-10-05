import json
from io import StringIO

from django.core.management import call_command

import pytest
from grants.models import Grant


@pytest.mark.django_db
def test_cypress_create_grant_defaults_create_one_grant():
    current_count = Grant.objects.count()

    call_command('cy_create_grants')

    assert Grant.objects.count() == current_count + 1


@pytest.mark.django_db
def test_command_outputs_grant_id_and_title_json_collection():
    out = StringIO()

    call_command('cy_create_grants', stdout=out)
    data = json.loads(out.getvalue())

    assert "id" in data[0]
    assert "title" in data[0]
