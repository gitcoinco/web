from django.contrib import admin

from quadraticlands.models import InitialTokenDistribution, MissionStatus, QuadLandsFAQ

class InitialTokenDistributionAdmin(admin.ModelAdmin):
    '''Needed to add raw_id_fields''' 
    raw_id_fields = ['profile']

admin.site.register(InitialTokenDistribution, InitialTokenDistributionAdmin)
admin.site.register(MissionStatus)
admin.site.register(QuadLandsFAQ)

