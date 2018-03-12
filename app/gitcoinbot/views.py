# -*- coding: utf-8 -*-
"""Define the Gitcoin Bot views.

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
import json

from django.conf import settings
from django.http import HttpResponse
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
    does_address_gitcoinbot = f"@{settings.GITHUB_API_USER}" in request_json['comment']['body']
    if (request_json['action'] == 'deleted') or request_json['sender']['login'] == 'gitcoinbot[bot]' or not does_address_gitcoinbot:
        # Gitcoinbot should not process these actions
        return HttpResponse(status=204)
    else:
        owner = request_json['repository']['owner']['login']
        repo = request_json['repository']['name']
        comment_id = request_json['comment']['id']
        comment_text = request_json['comment']['body']
        issue_id = request_json['issue']['number']
        installation_id = request_json['installation']['id']
        # sender = request_json['sender']['login']
        # issueURL = request_json['comment']['url']
        determine_response(owner, repo, comment_id, comment_text, issue_id, installation_id)
    return HttpResponse('Gitcoinbot Responded')
