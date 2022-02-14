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

import shutil

from celery.exceptions import MaxRetriesExceededError
from pathlib import Path
from unittest.mock import patch

import pytest

from django.core import mail

from app import settings
from dashboard.tests.factories import ProfileFactory, EarningFactory
from grants.tests.factories import GrantFactory
from marketing.tasks import export_earnings_to_csv, send_csv


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='gitcoin', password='password123')


@pytest.fixture
def profile(user):
    return ProfileFactory(user=user, handle='gitcoin')


@pytest.fixture
def grant(profile):
    return GrantFactory(admin_profile=profile)


@pytest.fixture
def earnings(profile, grant):
    return EarningFactory.create_batch(5, to_profile=profile, source=grant)


@pytest.mark.django_db
class TestExportEarningsToCSVTask:
    def test_export_earnings_to_csv(self, profile, grant, earnings):
        path = f'app/assets/tmp/user-earnings/{profile.handle}'

        assert len(list(Path(path).glob('*.csv'))) == 0
        export_earnings_to_csv(profile.user.pk, 'earnings')
        assert len(list(Path(path).glob('*.csv'))) == 1

        shutil.rmtree('app/assets/tmp/user-earnings/')

    def test_csv_has_proper_data(self, profile, grant, earnings):
        path = f'app/assets/tmp/user-earnings/{profile.handle}'
        export_earnings_to_csv(profile.user.pk, 'earnings')
        csv_path = list(Path(path).glob('*.csv'))[0]

        with open(csv_path, 'r') as file:
            data = file.readlines()

        headers = ['ID', 'Date', 'From', 'From Location', 'To', 'To Location', 'Type', 'Value In USD', 'TXID', 'Token Name', 'Token Value', 'URL']
        assert data[0] == ",".join(headers)+"\n"
        assert len(data) == 6
        assert len(data[1].split(',')) == len(headers)

        shutil.rmtree('app/assets/tmp/user-earnings/')

    def test_send_csv_is_called(self, profile, earnings):
        path = f'app/assets/tmp/user-earnings/{profile.handle}'

        with patch('marketing.tasks.send_csv') as send_csv_mock:
            export_earnings_to_csv(profile.user.pk, 'earnings')

            assert send_csv_mock.call_count == 1
            assert send_csv_mock.call_args[1]['user_profile'] == profile

        shutil.rmtree('app/assets/tmp/user-earnings/')


@pytest.mark.django_db
class TestSendCSV:
    def test_send_csv_email(self, profile):
        path = 'app/assets/tmp/test-file.csv'

        with patch('marketing.tasks.send_mail') as mock_send_mail:
            send_csv(path, profile)

            assert mock_send_mail.call_count == 1
            assert mock_send_mail.call_args[0][0] == settings.CONTACT_EMAIL
            assert mock_send_mail.call_args[0][1] == profile.user.email
            assert mock_send_mail.call_args[0][2] == 'Your Gitcoin CSV Download'

            assert mock_send_mail.call_args[1]['from_name'] == f'@{profile.handle}'
            assert mock_send_mail.call_args[1]['categories'] == ['transactional']
            assert mock_send_mail.call_args[1]['csv'] == path



