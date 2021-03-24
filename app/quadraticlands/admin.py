from django.contrib import admin

from quadraticlands.models import InitialTokenDistribution, MissionStatus, QuadLandsFAQ


class InitialtokenDistribution(admin.ModelAdmin):
    '''Setup initial dist admin'''
    raw_id_fields = ['profile'] 

admin.site.register(InitialTokenDistribution)
admin.site.register(MissionStatus)
admin.site.register(QuadLandsFAQ)

