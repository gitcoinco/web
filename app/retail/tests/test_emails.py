from unittest import mock

import pytest

from ..emails import render_start_work_new_applicant
from .factories.bounty_factory import BountyFactory
from .factories.interest_factory import InterestFactory


@pytest.mark.django_db
class TestRetailStartWorkNewApplicantEmail:
    def test_params_include_reject_worker_url(self):
        bounty = BountyFactory()
        interest = InterestFactory()

        with mock.patch('retail.emails.render_to_string') as mock_render:
            mock_render.return_value = "<html><body>I am an email</body></html>"

            render_start_work_new_applicant(interest, bounty)
            params = mock_render.call_args[0][1]

            assert 'reject_worker_url' in params
            assert '?mutate_worker_action=reject&worker=' in params['reject_worker_url']
