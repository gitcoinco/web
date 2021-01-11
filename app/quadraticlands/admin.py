from django.contrib import admin

from quadraticlands.models import Ballot, InitialTokenDistribution, MissionStatus, Proposal, QuadLandsFAQ

admin.site.register(InitialTokenDistribution)
admin.site.register(MissionStatus)
admin.site.register(QuadLandsFAQ)
admin.site.register(Proposal)
admin.site.register(Ballot)
