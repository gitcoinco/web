# -*- coding: utf-8 -*-
"""Define the Gitcoin Bot views.

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
import json

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .actions import determine_response


@csrf_exempt
@require_POST
def payload(request):
    """Handle the Github bot payload.

    Parse request.body bytes from github into json, retrieve relevant info
    and respond with appropriate message from gitcoinbot actions.

    Returns:
        HttpResponse: The confirmation of Github payload acceptance.

    """
    request_json = json.loads(request.body.decode('utf8'))
    comment_dict = request_json.get('comment', {})
    repo_dict = request_json.get('repository', {})
    sender_dict = request_json.get('sender', {})
    action = request_json.get('action', '')

    does_address_gitcoinbot = f"@{settings.GITHUB_API_USER}" in comment_dict.get('body', '')
    if action == 'deleted' or sender_dict.get('login', '') == 'gitcoinbot[bot]' or not does_address_gitcoinbot:
        # Gitcoinbot should not process these actions
        return HttpResponse(status=204)
    owner = repo_dict.get('owner', {}).get('login')
    repo = repo_dict.get('name')
    comment_id = comment_dict.get('id')
    comment_text = comment_dict.get('body')
    issue_id = request_json.get('issue', {}).get('number')
    installation_id = request_json.get('installation', {}).get('id')
    sender = request_json.get('sender', {}).get('login', '')
    determine_response(owner, repo, comment_id, comment_text, issue_id, installation_id, sender)
    return HttpResponse(_('Gitcoinbot Responded'))
