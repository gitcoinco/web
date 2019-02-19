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
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models.functions import Lower

from app.utils import sync_profile
from dashboard.models import Profile


def combine_profiles(p1, p2):
    # p2 is the delete profile, p1 is the save profile
    # switch if p2 has the user
    # TODO: refactor to use https://github.com/mighty-justice/django-super-deduper
    # instead
    if p2.user:
        p1, p2 = p2, p1

    p1.github_access_token = p2.github_access_token if p2.github_access_token else p1.github_access_token
    p1.slack_token = p2.slack_token if p2.slack_token else p1.slack_token
    p1.avatar = p2.active_avatar if p2.active_avatar else p1.active_avatar
    p1.slack_repos = p2.slack_repos if p2.slack_repos else p1.slack_repos
    p1.slack_channel = p2.slack_channel if p2.slack_channel else p1.slack_channel
    p1.email = p2.email if p2.email else p1.email
    p1.preferred_payout_address = p2.preferred_payout_address if p2.preferred_payout_address else p1.preferred_payout_address
    p1.max_tip_amount_usdt_per_tx = max(p1.max_tip_amount_usdt_per_tx, p2.max_tip_amount_usdt_per_tx)
    p1.max_tip_amount_usdt_per_week = max(p1.max_tip_amount_usdt_per_week, p2.max_tip_amount_usdt_per_week)
    p1.max_num_issues_start_work = max(p1.max_num_issues_start_work, p2.max_num_issues_start_work)
    p1.trust_profile = any([p1.trust_profile, p2.trust_profile])
    p1.hide_profile = False
    p1.suppress_leaderboard = any([p1.suppress_leaderboard, p2.suppress_leaderboard])
    p1.user = p2.user if p2.user else p1.user
    # tips, bounties, fulfillments, and interests , activities, actions
    for obj in p2.received_tips.all():
        obj.recipient_profile = p1
        obj.save()
    for obj in p2.sent_tips.all():
        obj.sender_profile = p1
        obj.save()
    for obj in p2.bounties_funded.all():
        obj.bounty_owner_profile = p1
        obj.save()
    for obj in p2.interested.all():
        obj.profile = p1
        obj.save()
    for obj in p2.fulfilled.all():
        obj.profile = p1
        obj.save()
    for obj in p2.activities.all():
        obj.profile = p1
        obj.save()
    for obj in p2.actions.all():
        obj.profile = p1
        obj.save()
    for obj in p2.token_approvals.all():
        obj.profile = p1
        obj.save()
    for obj in p2.votes.all():
        obj.profile = p1
        obj.save()
    for obj in p2.received_kudos.all():
        obj.recipient_profile = p1
        obj.save()
    for obj in p2.sent_kudos.all():
        obj.sender_profile = p1
        obj.save()
    for obj in p2.kudos_wallets.all():
        obj.profile = p1
        obj.save()
    p2.delete()
    p1.save()


class Command(BaseCommand):

    help = 'cleans up users who have duplicate profiles'

    def handle(self, *args, **options):
        whitespace_profiles = Profile.objects.filter(handle__endswith=' ')
        print(f" - {whitespace_profiles.count()} whitespace profiles")
        for profile in whitespace_profiles:
            profile.handle = profile.handle.strip()
            profile.save()

        at_profiles = Profile.objects.filter(handle__startswith='@')
        print(f" - {at_profiles.count()} at_profiles")
        for profile in at_profiles:
            profile.handle = profile.handle.replace('@', '')
            profile.save()

        dupes = Profile.objects.exclude(handle=None).annotate(handle_lower=Lower("handle")) \
            .values('handle_lower').annotate(handle_lower_count=Count('handle_lower')) \
            .filter(handle_lower_count__gt=1)
        print(f" - {dupes.count()} dupes")

        for dupe in dupes:
            handle = dupe['handle_lower']
            profiles = Profile.objects.filter(handle__iexact=handle).distinct("pk")
            print(f"combining {handle}: {profiles[0].pk} and {profiles[1].pk}")
            combine_profiles(profiles[0], profiles[1])

        # KO Hack 2018/12/10
        # For some reason, profiles keep getting set to hide_profile=True, even
        # when there's no form submissions on record for them.
        # this is a stopgap until we can figure out the root cause
        profiles = Profile.objects.filter(hide_profile=True, form_submission_records=[])
        for profile in profiles:
            profile.hide_profile = False
            profile.save()
            print(profile.handle)

        # KO Hack 2019/01/07
        # For some reason, these proiles keep getting
        # removed from their useres.  this mgmt command fixes that
        for user in User.objects.filter(profile__isnull=True):
            profiles = Profile.objects.filter(handle__iexact=user.username)
            if profiles.exists():
                print(user.username)
                profile = profiles.first()
                profile.user = user
                profile.save()
            else:
                sync_profile(user.username, user, hide_profile=True)
