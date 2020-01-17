from django.contrib import admin
from django.utils import timezone

from .models import Announcement, Comment, Flag, Like, Offer, OfferAction


# Register your models here.
class GenericAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']
    raw_id_fields = ['activity', 'profile']


class OfferActionAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']
    raw_id_fields = ['profile']


class OfferAdmin(admin.ModelAdmin):
    list_display = ['created_on', 'active_now', 'key', 'valid_from', 'valid_to', '__str__']
    raw_id_fields = ['persona', 'created_by']
    readonly_fields = ['active_now']

    def active_now(self, obj):
        if obj.valid_from and obj.valid_to:
            if obj.valid_from < timezone.now() and obj.valid_to > timezone.now():
                return "ACTIVE NOW"
        return "-"

    def response_change(self, request, obj):
        if "_copy_offer" in request.POST:
            obj.pk = None
            days = 1 if obj.key == 'daily' else 7
            if obj.key == 'monthly':
                days = 30
            obj.valid_from = timezone.now() - timezone.timedelta(days=days)
            while True:
                next_timestamp = obj.valid_from + timezone.timedelta(days=days)
                other_offers = Offer.objects.filter(valid_from__gte=obj.valid_from, valid_from__lt=next_timestamp, key=obj.key)
                if not other_offers.exists():
                    break
                obj.valid_from = next_timestamp
            obj.valid_from = obj.valid_from + timezone.timedelta(days=days)
            obj.valid_from = obj.valid_from - timezone.timedelta(hours=int(obj.valid_from.strftime('%H')))
            obj.valid_from = obj.valid_from - timezone.timedelta(minutes=int(obj.valid_from.strftime('%M')))
            obj.valid_from = obj.valid_from - timezone.timedelta(seconds=int(obj.valid_from.strftime('%S')))
            obj.valid_to = obj.valid_from + timezone.timedelta(days=days)
            self.message_user(request, f"Copied Object")

            obj.save()
        return super().response_change(request, obj)


class AnnounceAdmin(admin.ModelAdmin):
    list_display = ['created_on', 'valid_from', 'valid_to', '__str__']

admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferAction, OfferActionAdmin)
admin.site.register(Comment, GenericAdmin)
admin.site.register(Like, GenericAdmin)
admin.site.register(Flag, GenericAdmin)
admin.site.register(Announcement, AnnounceAdmin)
