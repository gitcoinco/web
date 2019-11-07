
from django.conf import settings
from django.utils import timezone
from economy.models import EncodeAnything
from django.core.management.base import BaseCommand
from dashboard.models import Profile
import json
import pprint

class Command(BaseCommand):

    help = 'outputs user data to cerebro ( https://docs.google.com/document/d/12-A8NabEJYzJqJtnHcG4ki1jAJ_K_OM8K_IAGbD8V7Y/edit# )'

    def handle(self, *args, **options):
        limit = 3

        profiles = Profile.objects.filter(hide_profile=False)
        if limit:
            profiles = profiles[:limit]
        outputs = []
        for profile in profiles:
            output = {
                "pk": profile.pk,
                "handle": profile.handle,
                "persona": profile.cascaded_persona,
                "activity_level": profile.activity_level,
                "reliability": profile.reliability,
                "output_time": timezone.now().strftime('%m/%d/%Y'),
                "last_visit": profile.last_visit.strftime('%m/%d/%Y'),
                "created_on": profile.created_on.strftime('%m/%d/%Y'),
                "success_rate": profile.success_rate,
                "total_funded_bounties_count": profile.as_dict.get('funded_bounties_count', 0),
                "total_count_bounties_completed": profile.as_dict.get('count_bounties_completed', 0),
                "total_kudos_sent_count": profile.as_dict.get('total_kudos_sent_count', 0),
                "total_kudos_received_count": profile.as_dict.get('total_kudos_received_count', 0),
                "total_grant_created": profile.as_dict.get('total_grant_created', 0),
                "total_grant_contributions": profile.as_dict.get('total_grant_contributions', 0),
                "total_grant_actions": profile.as_dict.get('total_grant_actions', 0),
                "total_tips_sent": profile.as_dict.get('total_tips_sent', 0),
                "total_tips_received": profile.as_dict.get('total_tips_received', 0),
                "total_quest_attempts": profile.as_dict.get('total_quest_attempts', 0),
                "total_quest_success": profile.as_dict.get('total_quest_success', 0),
                "total_bounties_work_started": profile.interested.count(),
                "avg_hourly_rate": profile.avg_hourly_rate,
                "keywords": profile.keywords,
                "works_with_funded": profile.as_dict.get('works_with_funded',[]),
                "works_with_collected": profile.as_dict.get('works_with_collected',[]),
                "organizations": profile.organizations,
                "github_data": profile.data,
                "job_type": profile.job_type,
                "job_salary": profile.job_salary,
                "job_location": profile.job_location,
                "job_salary": profile.job_salary,

            }
            outputs.append(output)
        print(json.dumps(outputs, cls=EncodeAnything))

