# -*- coding: utf-8 -*-
"""Define the Grant forms.

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
from django import forms
from django.utils.translation import gettext_lazy as _

from grants.models import Grant


class GrantForm(forms.ModelForm):
    """Define the Grant form logic."""

    class Meta:
        """Define the metadata for the Grant model form."""

        model = Grant
        fields = (
            'title', 'description', 'reference_url', 'github_project_url', 'logo', 'logo_svg', 'admin_address', 'deploy_tx_id',
            'cancel_tx_id', 'amount_received', 'token_address', 'contract_address', 'metadata', 'network',
            'required_gas_price', 'admin_profile', 'team_members'
        )
