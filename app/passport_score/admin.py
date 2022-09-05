from django.contrib import admin

from .models import GR15TrustScore

# Register your models here.


class GR15TrustScoreAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_last_apu_score",
        "get_max_apu_score",
        "get_trust_bonus",
        "last_apu_calculation_time",
        "max_apu_calculation_time",
        "trust_bonus_calculation_time",
        "stamps",
    )

    search_fields = ["user__username"]

    def get_last_apu_score(self, obj):
        return str(obj.last_apu_score)

    def get_max_apu_score(self, obj):
        return str(obj.max_apu_score)

    def get_trust_bonus(self, obj):
        return str(obj.trust_bonus)

    get_last_apu_score.admin_order_field = "last_apu_score"
    get_max_apu_score.admin_order_field = "max_apu_score"
    get_trust_bonus.admin_order_field = "trust_bonus"


admin.site.register(GR15TrustScore, GR15TrustScoreAdmin)
