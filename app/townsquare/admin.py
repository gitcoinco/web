from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Announcement, Comment, Flag, Like, Offer, OfferAction


# Register your models here.
class GenericAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']
    raw_id_fields = ['activity', 'profile']


class OfferActionAdmin(admin.ModelAdmin):
    list_display = ['created_on', 'github_created_on', 'from_ip_address', '__str__']
    raw_id_fields = ['profile']

    def github_created_on(self, instance):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(instance.profile.github_created_on)

    def from_ip_address(self, instance):
        end = instance.created_on + timezone.timedelta(hours=1)
        start = instance.created_on - timezone.timedelta(hours=1)
        visits = set(instance.profile.actions.filter(created_on__gt=start, created_on__lte=end).values_list('ip_address', flat=True))
        visits = [visit for visit in visits if visit]
        return " , ".join(visits)


class OfferAdmin(admin.ModelAdmin):
    list_display = ['created_on', 'active_now', 'key', 'valid_from', 'valid_to', '__str__', 'stats']
    raw_id_fields = ['persona', 'created_by']
    readonly_fields = ['active_now', 'stats']

    def active_now(self, obj):
        if obj.valid_from and obj.valid_to:
            if obj.valid_from < timezone.now() and obj.valid_to > timezone.now():
                return "ACTIVE NOW"
        return "-"

    def stats(self, obj):
        views = obj.view_count
        click = obj.actions.filter(what='click').count()
        go = obj.actions.filter(what='go').count()
        pct_go = round(go/click*100,0) if click else "-"
        pct_click = round(click/views*100,0) if views else "-"
        return format_html(f"views => click => go<BR>{views} => {click} ({pct_click}%) => {go} ({pct_go}%)")

    def response_change(self, request, obj):
        if "_copy_offer" in request.POST:
            obj.pk = None
            days = 1 if obj.key == 'daily' else 7
            if obj.key == 'monthly':
                days = 30
            obj.valid_from = timezone.now() - timezone.timedelta(days=days)
            obj.view_count = 0
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
