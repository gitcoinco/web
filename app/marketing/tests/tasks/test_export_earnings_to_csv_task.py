# -*- coding: utf-8 -*-
"""Handle marketing tasks related tests.

Copyright (C) 2021 Gitcoin Core

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
from pathlib import Path
import glob
import os
from unittest.mock import patch

import pytest

from dashboard.tests.factories import ProfileFactory, EarningFactory
from grants.tests.factories import GrantFactory
from marketing.tasks import export_earnings_to_csv


@pytest.mark.django_db
class TestExportEarningsToCSVTask:

    def test_export_earnings_to_csv(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        profile = ProfileFactory(user=user, handle='gitcoin')
        grant = GrantFactory(admin_profile=profile)
        earnings = EarningFactory.create_batch(5, to_profile=profile, source=grant)

        path = 'app/assets/tmp/user-earnings/gitcoin'

        assert len(list(Path(path).glob('*.csv'))) == 0

        export_earnings_to_csv(user.pk, 'earnings')

        assert len(list(Path(path).glob('*.csv'))) == 1
