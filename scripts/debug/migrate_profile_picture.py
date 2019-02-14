from app.utils import sync_profile
from avatar.utils import get_avatar
from dashboard.models import Profile

handle='whalechat'
profile = Profile.objects.get(handle=handle)
avatar = profile.avatar_baseavatar_related.first()
avatar.delete()
sync_profile(profile.handle)
