from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

import pytz
from economy.models import ConversionRate
from gas.models import GasProfile
from github.utils import get_issues, get_user
from marketing.models import Stat


class Command(BaseCommand):

    help = 'backfills analytics that havent been pull by pull stats'

    def handle(self, *args, **options):

        repos = [
        ]

        for org in ['bitcoin', 'gitcoinco', 'ethereum']:
            for repo in get_user(org, '/repos'):
                repos.append((org, repo['name']))
        print(repos)
        for org, repo in repos:
            issues = []
            cont = True
            page = 1
            while cont:
                new_issues = get_issues(org, repo, page, 'all')
                issues = issues + new_issues
                page += 1
                cont = len(new_issues)
            print(len(issues))

            for x in range(0, len(issues)):
                issues[x]['created_at'] = datetime.strptime(issues[x]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                issues[x]['created_at'] = issues[x]['created_at'].replace(tzinfo=pytz.utc)

            that_time = timezone.now()
            while True:
                that_time = that_time - timezone.timedelta(hours=1)
                val = len([x for x in issues if x['created_at'] < that_time])
                key = f"github_issues_{org}_{repo}"
                try:
                    Stat.objects.create(
                        created_on=that_time,
                        key=key,
                        val=(val),
                        )
                except:
                    pass
                if not val:
                    break
                print(that_time, key, val)
