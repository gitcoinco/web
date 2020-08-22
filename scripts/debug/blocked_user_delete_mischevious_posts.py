handle = 'miscreant1'
from dashboard.models import Profile
profile = Profile.objects.get(handle=handle)
profile.activities.all().delete()
profile.other_activities.all().delete()
profile.comments.all().delete()