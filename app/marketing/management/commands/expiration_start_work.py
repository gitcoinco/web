'''
    Copyright (C) 2017 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, Interest
from github.utils import get_issue_comments, issue_number, org_name, repo_name
from marketing.mails import bounty_startwork_expire_warning, bounty_startwork_expired


class Command(BaseCommand):

    help = 'lets a user know that they expressed interest in an issue and kicks them to do something about it'

    def handle(self, *args, **options):
        num_days_back_to_warn = 3
        num_days_back_to_delete_interest = 7

        days = [i * 3 for i in range(1, 15)]
        if settings.DEBUG:
            days = range(1, 1000)
        for day in days:
            interests = Interest.objects.filter(
                created__gte=(timezone.now() - timezone.timedelta(days=(day+1))),
                created__lt=(timezone.now() - timezone.timedelta(days=day)),
            ).all()
            print('day {} got {} interests'.format(day, interests.count()))
            for interest in interests:
                for bounty in Bounty.objects.filter(interested=interest, current_bounty=True, idx_status__in=['open', 'started']):
                    print("{} is interested in {}".format(interest, bounty))
                    try:
                        owner = org_name(bounty.github_url)
                        repo = repo_name(bounty.github_url)
                        issue_num = issue_number(bounty.github_url)
                        comments = get_issue_comments(owner, repo, issue_num)
                        comments_by_interested_party = [comment for comment in comments if comment['user']['login'] == interest.profile.handle]
                        should_warn_user = False
                        should_delete_interest = False
                        last_heard_from_user_days = None

                        if len(comments_by_interested_party) == 0:
                            should_warn_user = True
                            should_delete_interest = False
                        else:
                            # example format: 2018-01-26T17:56:31Z'
                            comment_times = [datetime.strptime(comment['created_at'], '%Y-%m-%dT%H:%M:%SZ') for comment in comments_by_interested_party]
                            last_comment_by_user = max(comment_times)

                            # if user hasn't commented since they expressed interest, handled this condition
                            # per https://github.com/gitcoinco/web/issues/462#issuecomment-368384384
                            if last_comment_by_user < interest.created.replace(tzinfo=None):
                                last_comment_by_user = interest.created.replace(tzinfo=None)

                            # some small calcs
                            delta_now_vs_last_comment = datetime.now() - last_comment_by_user
                            last_heard_from_user_days = delta_now_vs_last_comment.days

                            # decide action params
                            should_warn_user = last_heard_from_user_days >= num_days_back_to_warn
                            should_delete_interest = last_heard_from_user_days >= num_days_back_to_delete_interest

                            print(f"- its been {last_heard_from_user_days} days since we heard from the user")

                        if should_delete_interest:
                            print('executing should_delete_interest for {}'.format(interest.pk))
                            bounty_startwork_expired(interest.profile.email, bounty, interest, last_heard_from_user_days)
                            interest.delete()

                        elif should_warn_user:
                            print('executing should_warn_user for {}'.format(interest.pk))
                            bounty_startwork_expire_warning(interest.profile.email, bounty, interest, last_heard_from_user_days)

                    except Exception as e:
                        print(e)
