# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from gitcoinbot.actions import determine_response


@csrf_exempt
def payload(request):
    '''Parse request.body bytes from github into json, retrieve relevant info
    and respond with appropriate message from gitcoinbot actions
    '''

    if request.method == "POST":
        request_json = json.loads(request.body.decode('utf8'))
        if (request_json['action'] == 'deleted') or request_json['sender']['login'] == 'gitcoinbot[bot]':
            # Gitcoinbot should not process these actions
            return HttpResponse(status=204)
        else:
            issueURL = request_json['comment']['url']
            owner = request_json['repository']['owner']['login']
            repo = request_json['repository']['name']
            comment_id = request_json['comment']['id']
            comment_text = request_json['comment']['body']
            issue_id = request_json['issue']['number']
            sender = request_json['sender']['login']
            installation_id = request_json['installation']['id']

            determine_response(owner, repo, comment_id,comment_text, issue_id,
                installation_id)

            return HttpResponse('Gitcoinbot Responded')
