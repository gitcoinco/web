# -*- coding: utf-8 -*-
"""Handle marketing model related tests.

Copyright (C) 2019 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from marketing.models import EmailEvent
from test_plus.test import TestCase


class MarketingModelsTest(TestCase):
    """Define tests for marketing models."""

    def setUp(self):
        """Perform setup for the testcase."""
        pass

    @staticmethod
    def test_email_event():
        """Test the marketing email event model."""
        categories = ['category 1', 'category 2', 'category 3']
        email_event = EmailEvent.objects.create(
            email="test@example.com",
            event="test_event",
            categories=categories,
            ip_address=None
        )

        assert len(email_event.categories) == 3
        assert email_event.categories[0] == 'category 1'
        assert email_event.categories[1] == 'category 2'
        assert email_event.categories[2] == 'category 3'
        assert EmailEvent.objects.filter(categories__contains=['category 3']).exists()
