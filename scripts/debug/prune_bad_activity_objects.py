#deletes the None None activity feed items in the newsfeed.  No idea where they come from, but this at least keeps them from showing up too long

import time

from django.utils import timezone

from dashboard.models import Activity

then = timezone.now() - timezone.timedelta(minutes=60)
activities = Activity.objects.filter(activity_type='status_update', metadata__title=None, created_on__gt=then).order_by('-pk')
activities.delete()
