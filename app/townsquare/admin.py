from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Announcement, Comment, Flag, Like, MatchRanking, MatchRound, Offer, OfferAction, PinnedPost, SquelchProfile,
    SuggestedAction,
)


# Register your models here.
class GenericAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']
    raw_id_fields = ['activity', 'profile']


class SquelchProfileAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']
    raw_id_fields = ['profile']
    search_fields = ['profile__handle']


class SuggestedActionAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']


class ActuallyGenericAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']


class MatchRankingAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']
    raw_id_fields = ['profile', 'round']

class PinnedPostAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']
    raw_id_fields = ['user', 'activity']
    fields = ['what']

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
    list_display = ['created_on', 'active_now', 'key', 'valid_from', 'valid_to', '__str__', 'stats', 'background_preview_small']
    raw_id_fields = ['persona', 'created_by']
    readonly_fields = ['active_now', 'stats', 'background_preview', 'schedule_preview']

    def active_now(self, obj):
        if obj.valid_from and obj.valid_to:
            if obj.valid_from < timezone.now() and obj.valid_to > timezone.now():
                return "ACTIVE NOW"
        return "-"

    def background_preview(self, instance, size=400):
        html = ''
        for ext in ['jpeg']:
            url = f'/static/v2/images/quests/backs/{instance.style}.{ext}'
            html += f"<img style='max-width: {size}px;' src='{url}'>"
        return format_html(html)

    def schedule_preview(self, instance, size=400):
        import pytz
        html = "<table style='max-width:700px; overflow-x: scroll;'>"
        for _type in ['monthly', 'weekly', 'daily', 'secret', 'random', 'top']:
            days = 1
            start = timezone.now() - timezone.timedelta(days=5)
            current = start
            end = timezone.now() + timezone.timedelta(days=45)
            html += f"<tr>"
            html += f"<td>{_type}</td>"
            while current < end:
                next_current = current + timezone.timedelta(days=days)
                cursor = current + timezone.timedelta(hours=1)
                has_offer = Offer.objects.filter(key=_type, valid_from__lte=cursor, valid_to__gt=cursor)
                is_today = timezone.now().strftime('%m/%d') == cursor.strftime('%m/%d')
                default_color = '#eeeeee' if is_today else "white"
                color = 'green' if has_offer.exists() else default_color
                if has_offer.filter(pk=instance.pk):
                    color='red'
                label = f"{current.strftime('%m/%d')}"
                if has_offer.exists():
                    url = has_offer.first().admin_url
                    label = f"<a style='color:white' href={url}>{label}</a>"
                html += f"<td style='background-color:{color}; padding: 2px; font-size: 10px; border: 1px solid #eee;' colspan={days}>{label}</td>"
                current = next_current
            html += f"</tr>"

        html += "</table>"
        return format_html(html)

    def background_preview_small(self, instance):
        return self.background_preview(instance, 120);

    def stats(self, obj):
        views = obj.view_count
        click = obj.actions.filter(what='click').count()
        go = obj.actions.filter(what='go').count()
        pct_go = round(go/click*100,0) if click else "-"
        pct_click = round(click/views*100,0) if views else "-"
        return format_html(f"views => click => go<BR>{views} => {click} ({pct_click}%) => {go} ({pct_go}%)")

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        if "_copy_offer" in request.POST:
            obj.pk = None
            obj.view_count = 0
            obj.valid_to, obj.valid_from = schedule_helper(obj)
            self.message_user(request, f"Copied Object")
            obj.save()
        return redirect(obj.admin_url)
        if "_schedule_offer" in request.POST:
            obj.valid_to, obj.valid_from = schedule_helper(obj)
            print(obj.valid_to, obj.valid_from)
            self.message_user(request, f"Scheduled Object")
            obj.save()
        return redirect(obj.admin_url)


def schedule_helper(obj):
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
    return obj.valid_to, obj.valid_from


class AnnounceAdmin(admin.ModelAdmin):
    list_display = ['created_on', 'valid_from', 'valid_to', '__str__']

admin.site.register(SuggestedAction, SuggestedActionAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(SquelchProfile, SquelchProfileAdmin)
admin.site.register(OfferAction, OfferActionAdmin)
admin.site.register(Comment, GenericAdmin)
admin.site.register(Like, GenericAdmin)
admin.site.register(Flag, GenericAdmin)
admin.site.register(PinnedPost, PinnedPostAdmin)
admin.site.register(MatchRound, ActuallyGenericAdmin)
admin.site.register(MatchRanking, MatchRankingAdmin)
admin.site.register(Announcement, AnnounceAdmin)
