'''
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

'''

import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from git.utils import (
    get_gh_notifications, get_issue_comments, issue_number, org_name, post_issue_comment_reaction, repo_name,
)
from github import RateLimitExceededException


class Command(BaseCommand):

    help = 'gets gitcoinbot notifications and responds if the user needs to install the app to get them to work'

    def handle(self, *args, **options):
        notifications = get_gh_notifications()
        try:
            print('Notifications Count: ', notifications.totalCount)
            for notification in notifications:
                if hasattr(notification, '_subject') and notification.reason == 'mention':
                    try:
                        url = notification.subject.url
                        url = url.replace('/repos', '')
                        url = url.replace('//api.github', '//github')
                        latest_comment_url = notification.subject.latest_comment_url
                        if latest_comment_url is None:
                            print("no latest comment url")
                            continue
                        _org_name = org_name(url)
                        _repo_name = repo_name(url)
                        _issue_number = issue_number(url)
                        if not latest_comment_url:
                            continue
                        _comment_id = latest_comment_url.split('/')[-1]
                        comment = get_issue_comments(_org_name, _repo_name, _issue_number, _comment_id)
                        does_mention_gitcoinbot = settings.GITHUB_API_USER in comment.get('body', '')
                        if comment.get('message', '') == "Not Found":
                            print("comment was not found")
                        elif not does_mention_gitcoinbot:
                            print("does not mention gitcoinbot")
                        else:
                            comment_from = comment['user']['login']
                            num_reactions = comment['reactions']['total_count']
                            print(_org_name, _repo_name, _issue_number, _comment_id, num_reactions, comment_from)
                            is_from_gitcoinbot = settings.GITHUB_API_USER in comment_from
                            if num_reactions == 0 and not is_from_gitcoinbot:
                                print("unprocessed")
                                post_issue_comment_reaction(_org_name, _repo_name, _comment_id, 'heart')
                    except RateLimitExceededException as e:
                        logging.debug(e)
                        print(e)
                        time.sleep(60)
                    except Exception as e:
                        logging.exception(e)
                        print(e)
        except RateLimitExceededException as e:
            logging.debug(e)
            print(e)
        except AttributeError as e:
            logging.debug(e)
            print(e)
