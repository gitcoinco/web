from app.utils import sync_profile
from avatar.utils import get_avatar
from dashboard.models import Profile

handle='proofsuite'
profile = Profile.objects.get(handle=handle)
avatar = profile.avatar_baseavatar_related.first()
if avatar:
    avatar.delete()
sync_profile(profile.handle)
