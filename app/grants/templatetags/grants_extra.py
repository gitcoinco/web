# -*- coding: utf-8 -*-
"""Define the add_url_schema template tag to allow cleaning up url in templates.

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
from django import template

from grants.models import Contribution, Grant

register = template.Library()


@register.filter
def addstr(value, arg):
    """Concats argument to string.

    Args:
        value (str): Original string
        arg (str): String to be concated

    Usage:
        {{ value|addstr(arg) }}

    Returns:
        str: The concatenated string.

    """
    return str(value) + str(arg)


@register.filter
def modulo(num, val):
    """Get the modulo of the provided number and value.

    Args:
        num (int): Something describing the number.
        val (int): Something describing the value.

    Usage:
        {{ num|modulo(val) }}

    Returns:
        int: The modulo of number and value.

    """
    return num % val


@register.filter
def remove_duplication(contributions):
    """Get the contribution list without duplication.

    Args:
        contributions (QuerySet<Contribution>): Something describing the contributions.

    Usage:
        {{ contributions|remove_duplication }}

    Returns:
        list: the contribution list without duplication.

    """
    handle_set = list()
    result = list()

    for contribution in contributions:
        if contribution.tx_cleared and contribution.success:
            handle = contribution.subscription.contributor_profile.handle
            if handle not in handle_set:
                temp_result = list()
                handle_set.append(handle)
                temp_result.append(handle)
                temp_result.append(contribution.subscription.contributor_profile.avatar_url)
                result.append(temp_result)

    return result


@register.filter
def remove_duplication_by_id(grant_id):
    """Get the contribution list without duplication by grant id.

        Args:
            grant_id (int): Grant index.

        Usage:
            {{ grant_id|remove_duplication_by_id }}

        Returns:
            list: the contribution list without duplication.

        """
    grant = Grant.objects.prefetch_related('subscriptions').get(pk=grant_id)
    contributions = Contribution.objects.filter(subscription__in=grant.subscriptions.all())

    return remove_duplication(contributions)
