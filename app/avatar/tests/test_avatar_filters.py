# -*- coding: utf-8 -*-
"""Define the is_in_list template tag to allow if in list checking in templates.

Copyright (C) 2018 Gitcoin Core

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
from django.contrib.auth.models import User

from avatar.templatetags.avatar_option_classes import avatar_option_classes
from avatar.utils import get_avatar_context_for_user
from test_plus.test import TestCase


class AvatarFilterTest(TestCase):
    """Define tests for avatar filters."""

    @staticmethod
    def test_avatar_option_classes():
        user = User(username="gitcoin")
        clothing_section = get_avatar_context_for_user(user)['sections'][6]
        classes = avatar_option_classes("robe", clothing_section)
        classes == "payment_required not_paid"
