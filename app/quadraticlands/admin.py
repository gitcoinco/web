from django.contrib import admin

from quadraticlands.models import (
    Game, GameFeed, GamePlayer, GTCSteward, InitialTokenDistribution, MissionStatus, QLVote, QuadLandsFAQ, SchwagCoupon,
)


class InitialTokenDistributionAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    search_fields = ['profile__handle']
    list_display = ['id', 'profile', 'claim_total']


class MissionStatusAdmin(admin.ModelAdmin):
    search_fields = ['profile__handle']
    list_display = ['id', 'profile', 'proof_of_use', 'proof_of_receive', 'proof_of_knowledge']
    raw_id_fields = ['profile']


class GTCStewardAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    search_fields = ['profile__handle']
    list_display = ['id', 'profile', 'real_name', 'profile_link']


class QuadLandsFAQAdmin(admin.ModelAdmin):
    list_display = ['id', 'position', 'question']


class QLVoteAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    list_display = ['id', 'profile']


class SchwagCouponAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    search_fields = ['profile__handle', 'coupon_code', 'discount_type']
    list_display = ['id', 'discount_type', 'coupon_code', 'profile']

class GamePlayerAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile', 'game']
    search_fields = ['profile__handle', 'game__title']

class GameFeedAdmin(admin.ModelAdmin):
    raw_id_fields = ['player', 'game']
    search_fields = ['player__handle', 'game__title']

class GameAdmin(admin.ModelAdmin):
    search_fields = ['title']


admin.site.register(Game, GameAdmin)
admin.site.register(GamePlayer, GamePlayerAdmin)
admin.site.register(GameFeed, GameFeedAdmin)
admin.site.register(InitialTokenDistribution, InitialTokenDistributionAdmin)
admin.site.register(MissionStatus, MissionStatusAdmin)
admin.site.register(QuadLandsFAQ, QuadLandsFAQAdmin)
admin.site.register(GTCSteward, GTCStewardAdmin)
admin.site.register(QLVote, QLVoteAdmin)
admin.site.register(SchwagCoupon, SchwagCouponAdmin)
