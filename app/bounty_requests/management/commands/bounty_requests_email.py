'''
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

'''

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bounty_requests.models import BountyRequest, BountyRequestMeta
from marketing.mails import bounty_request_feedback


class Command(BaseCommand):

    help = 'Dispatches email feedback for funded Bounty Requests at most once in 8 weeks.'

    def handle(self, *args, **options):
        now = timezone.now()
        delta = timedelta(weeks=8)
        bounty_requests = BountyRequest.objects.filter(
            status=BountyRequest.STATUS_FUNDED,
            created_on__lte=now - delta,
        )

        for request in bounty_requests:
            profile = request.requested_by

            if not profile or not profile.email:
                continue

            meta = BountyRequestMeta.objects.filter(profile=profile).last()

            if not meta:
                meta = BountyRequestMeta(profile=profile)

            if not meta.last_feedback_sent or (now - meta.last_feedback_sent) >= delta:
                bounty_request_feedback(profile)
                meta.last_feedback_sent = now
                meta.save()
