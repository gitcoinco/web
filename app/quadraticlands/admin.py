from django.contrib import admin

from quadraticlands.models import Choice, InitialTokenDistribution, MissionStatus, Proposal, QuadLandsFAQ, Question

admin.site.register(InitialTokenDistribution)
admin.site.register(MissionStatus)
admin.site.register(QuadLandsFAQ)
admin.site.register(Proposal)
admin.site.register(Question)
admin.site.register(Choice)
