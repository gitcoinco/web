'''
    Copyright (C) 2017 Gitcoin Core

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

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models.functions import Lower

from marketing.models import EmailSubscriber


def combine_emails(e1, e2):
    # e2 is the delete profile, e1 is the save profile
    if e2.metadata and not e1.metadata:
        e1, ee2 = e2, e1

    e1.source = e2.source if e2.source else e1.source
    e1.active = e2.active if e2.active else e1.active
    e1.newsletter = e2.newsletter if e2.newsletter else e1.newsletter
    e1.preferences = e2.preferences if e2.preferences else e1.preferences
    e1.metadata = e2.metadata if e2.metadata else e1.metadata
    e1.priv = e2.priv if e2.priv else e1.priv
    e1.github = e2.github if e2.github else e1.github
    e1.keywords = e2.keywords if e2.keywords else e1.keywords
    e1.profile = e2.profile if e2.profile else e1.profile
    e1.form_submission_records = e2.form_submission_records if e2.form_submission_records else e1.form_submission_records
    e2.delete()
    e1.save()



class Command(BaseCommand):

    help = 'cleans up users who have duplicate emails'

    def handle(self, *args, **options):

        dupes = EmailSubscriber.objects.exclude(email=None).annotate(email_lower=Lower("email")).values('email_lower').annotate(email_lower_count=Count('email_lower')).filter(email_lower_count__gt=1)
        print(f" - {dupes.count()} dupes")

        for dupe in dupes:
            handle = dupe['email_lower']
            profiles = EmailSubscriber.objects.filter(email__iexact=handle).distinct("pk")
            print(f"combining {handle}: {profiles[0].pk} and {profiles[1].pk}")
            combine_emails(profiles[0], profiles[1])
