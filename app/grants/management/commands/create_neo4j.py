from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import Earning
from django.utils import timezone
import re

class Command(BaseCommand):

    help = 'migrates the activity on one grant to another'

    def handle(self, *args, **options):
        end_date = timezone.now()
        start_date = timezone.now() - timezone.timedelta(days=90)
        _type = 'grant'
        limit = 20000
        target_user = ''

        earnings = Earning.objects.filter(created_on__gt=start_date, created_on__lt=end_date)
        from django.contrib.contenttypes.models import ContentType
        mapping = {
            'grant': ContentType.objects.get(app_label='grants', model='contribution'),
            'kudos': ContentType.objects.get(app_label='kudos', model='kudostransfer'),
            'tip': ContentType.objects.get(app_label='dashboard', model='tip'),
            'bounty': ContentType.objects.get(app_label='dashboard', model='bountyfulfillment'),
        }
        earnings = earnings.filter(source_type=mapping[_type])
        earnings = earnings[0:limit]
        curly = '{'
        ecurly = '}'

        declared_users = {}
        declared_admins = {}

        for earning in earnings.iterator():
            from_profile = earning.from_profile
            to_profile = earning.to_profile
            grant = earning.source.subscription
            grant = grant.grant
            admin_profile = grant.admin_profile

            title = grant.title.replace(' ', '_')
            title = "grant_" + re.sub(r'\W+', '', title)

            from_profile_handle = "user_" + re.sub(r'\W+', '', from_profile.handle)
            to_profile_handle = "user_" + re.sub(r'\W+', '', to_profile.handle)
            admin_profile_handle = "user_" + re.sub(r'\W+', '', admin_profile.handle)

            if not target_user:
                target_user = from_profile_handle

            if admin_profile_handle not in declared_users.keys():
                print(f"CREATE ({admin_profile_handle}:Person {curly}name:'{admin_profile_handle}', pk:{admin_profile.pk}{ecurly})")
                declared_users[admin_profile_handle] = 1
            if from_profile_handle not in declared_users.keys():
                print(f"CREATE ({from_profile_handle}:Person {curly}name:'{from_profile_handle}', pk:{from_profile.pk}{ecurly})")
                declared_users[from_profile_handle] = 1
            if to_profile_handle not in declared_users.keys():
                print(f"CREATE ({to_profile_handle}:Person {curly}name:'{to_profile_handle}', pk:{to_profile.pk}{ecurly})")
                declared_users[to_profile_handle] = 1
            if title not in declared_users.keys():
                print(f"CREATE ({title}:Grant {curly}name:'{title}', pk:{grant.pk}{ecurly})")
                declared_users[title] = 1
            print(f"CREATE ({from_profile_handle})-[:CONTRIBUTED_TO {curly}amount:[\"{earning.value_usd}\"]{ecurly}]->({title})")
            if title not in declared_admins.keys():
                print(f"CREATE ({admin_profile_handle})-[:ADMIN_OF {curly}amount:[\"{earning.value_usd}\"]{ecurly}]->({title})")
                declared_admins[title] = 1

        print(f"""
WITH {target_user} as a
MATCH (c)-[:CONTRIBUTED_TO]->(m)<-[:ADMIN_OF]-(d) RETURN a,m,d LIMIT {limit};
            """)
