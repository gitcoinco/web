from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

import townsquare.clr as clr
from economy.models import SuperModel


class Like(SuperModel):
    """A like is an indication of a favored activity feed item"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='likes', blank=True)
    activity = models.ForeignKey('dashboard.Activity',
        on_delete=models.CASCADE, related_name='likes', blank=True, db_index=True)

    def __str__(self):
        return f"Like of {self.activity.pk} by {self.profile.handle}"

    @property
    def url(self):
        return self.activity.url

    def get_absolute_url(self):
        return self.activity.url


class Flag(SuperModel):
    """A Flag is an indication of a flagged activity feed item"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='flags', blank=True)
    activity = models.ForeignKey('dashboard.Activity',
        on_delete=models.CASCADE, related_name='flags', blank=True, db_index=True)

    def __str__(self):
        return f"Flag of {self.activity.pk} by {self.profile.handle}"

    @property
    def url(self):
        return self.activity.url

    def get_absolute_url(self):
        return self.activity.url


class Comment(SuperModel):
    """An comment on an activity feed item"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='comments', blank=True)
    activity = models.ForeignKey('dashboard.Activity',
        on_delete=models.CASCADE, related_name='comments', blank=True, db_index=True)
    comment = models.TextField(default='', blank=True)
    tip = models.ForeignKey(
        'dashboard.Tip',
        related_name='awards',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    likes = ArrayField(models.IntegerField(), default=list, blank=True) #pks of users who like this post
    likes_handles = ArrayField(models.CharField(max_length=200, blank=True), default=list, blank=True) #handles of users who like this post
    tip_count_eth = models.DecimalField(default=0, decimal_places=5, max_digits=50)
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment of {self.activity.pk} by {self.profile.handle}: {self.comment}"

    @property
    def profile_handle(self):
        return self.profile.handle

    @property
    def redeem_link(self):
        if self.tip:
            return self.tip.receive_url
        return ''

    @property
    def tip_able(self):
        return self.activity.metadata.get("tip_able", False)

    @property
    def url(self):
        return self.activity.url

    @property
    def get_tip_count_eth(self):
        from dashboard.models import Tip
        network = 'rinkeby' if settings.DEBUG else 'mainnet'
        tips = Tip.objects.filter(comments_priv=f"comment:{self.pk}", network=network)
        return sum([tip.value_in_eth for tip in tips])

    def get_absolute_url(self):
        return self.url


@receiver(pre_save, sender=Comment, dispatch_uid="pre_save_comment")
def presave_comment(sender, instance, **kwargs):
    from dashboard.models import Profile
    instance.likes_handles = list(Profile.objects.filter(pk__in=instance.likes).values_list('handle', flat=True))
    instance.tip_count_eth = instance.get_tip_count_eth


@receiver(post_save, sender=Comment, dispatch_uid="post_save_comment")
def postsave_comment(sender, instance, created, **kwargs):
    from townsquare.tasks import send_comment_email
    if created:
        if not instance.is_edited:
            send_comment_email.delay(instance.pk)


class OfferQuerySet(models.QuerySet):
    """Handle the manager queryset for Offers."""

    def current(self):
        """Filter results down to current offers only."""
        timestamp = timezone.now()
        timestamp -= timezone.timedelta(microseconds=timestamp.microsecond)
        timestamp -= timezone.timedelta(seconds=int(timestamp.strftime('%S')))
        timestamp -= timezone.timedelta(minutes=int(timestamp.strftime('%M')))
        return self.filter(valid_from__lte=timestamp, valid_to__gt=timestamp, public=True)

num_backgrounds = 33


class Offer(SuperModel):
    """An offer"""
    OFFER_TYPES = [
        ('secret', 'secret'),
        ('random', 'random'),
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
        ('other', 'other'),
        ('top', 'top'),
    ]
    STYLES = [
        ('red', 'red'),
        ('green', 'green'),
        ('blue', 'blue'),
    ] + [(f'back{i}', f'back{i}') for i in range(0, num_backgrounds + 1)]

    from_name = models.CharField(max_length=50, blank=True)
    from_link = models.URLField(blank=True)
    title = models.TextField(default='', blank=True)
    desc = models.TextField(default='', blank=True)
    url = models.URLField(db_index=True)
    valid_from = models.DateTimeField(db_index=True)
    valid_to = models.DateTimeField(db_index=True)
    key = models.CharField(max_length=50, db_index=True, choices=OFFER_TYPES)
    style = models.CharField(max_length=50, db_index=True, choices=STYLES, default='announce1')
    persona = models.ForeignKey('kudos.Token', blank=True, null=True, related_name='offers', on_delete=models.SET_NULL)
    created_by = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='offers_created', blank=True, null=True)
    public = models.BooleanField(help_text='Is this available publicly yet?', default=True)
    view_count = models.IntegerField(default=0, db_index=True)
    amount = models.CharField(max_length=50, blank=True)
    comments_admin = models.TextField(default='', blank=True)

    # Offer QuerySet Manager
    objects = OfferQuerySet.as_manager()

    def __str__(self):
        return f"{self.key} / {self.title}"

    @property
    def view_url(self):
        slug = slugify(self.title)
        return f'/action/{self.pk}/{slug}'

    def get_absolute_url(self):
        return self.view_url + '?preview=1'

    @property
    def go_url(self):
        return self.view_url + '/go'

    @property
    def decline_url(self):
        return self.view_url + '/decline'


class OfferAction(SuperModel):
    """An offer action, where a click or a completion"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='offeractions', blank=True)
    offer = models.ForeignKey('townsquare.Offer',
        on_delete=models.CASCADE, related_name='actions', blank=True)
    what = models.CharField(max_length=50, db_index=True) # click, completion, etc

    def __str__(self):
        return f"{self.profile.handle} => {self.what} => {self.offer.title}"


class AnnounceQuerySet(models.QuerySet):
    """Handle the manager queryset for Announcements."""

    def current(self):
        """Filter results down to current offers only."""
        return self.filter(valid_from__lte=timezone.now(), valid_to__gt=timezone.now())


class Announcement(SuperModel):
    """An Announcement to the users to be displayed on town square."""

    _TYPES = [
        ('townsquare', 'townsquare'),
        ('header', 'header'),
        ('footer', 'footer'),
        ('founders_note_daily_email', 'founders_note_daily_email'),
        ('grants', 'grants'),
    ]
    key = models.CharField(max_length=50, db_index=True, choices=_TYPES)
    title = models.TextField(default='', blank=True)
    desc = models.TextField(default='', blank=True)
    valid_from = models.DateTimeField(db_index=True)
    valid_to = models.DateTimeField(db_index=True)
    rank = models.IntegerField(default=0)

    STYLES = [
        ('primary', 'primary'),
        ('secondary', 'secondary'),
        ('success', 'success'),
        ('danger', 'danger'),
        ('warning', 'warning'),
        ('info', 'info'),
        ('light', 'light'),
        ('dark', 'dark'),
        ('white', 'white'),
    ]

    style = models.CharField(max_length=50, db_index=True, choices=STYLES, default='announce1', help_text='https://getbootstrap.com/docs/4.0/utilities/colors/')

    # Bounty QuerySet Manager
    objects = AnnounceQuerySet.as_manager()
    def __str__(self):
        return f"{self.created_on} => {self.title}"

    @property
    def salt(self):
        if self.pk < 49:
            return self.rank
        return self.pk

class MatchRoundQuerySet(models.QuerySet):
    """Handle the manager queryset for MatchRanking."""

    def current(self):
        """Filter results down to current offers only."""
        return self.filter(valid_from__lte=timezone.now(), valid_to__gt=timezone.now())


class MatchRound(SuperModel):

    valid_from = models.DateTimeField(db_index=True)
    valid_to = models.DateTimeField(db_index=True)
    number = models.IntegerField(default=1)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=50)

    # Offer QuerySet Manager
    objects = MatchRoundQuerySet.as_manager()

    def __str__(self):
        return f"Round {self.number} from {self.valid_from} to {self.valid_to}"

    @property
    def url(self):
        return self.activity.url

    def get_absolute_url(self):
        return self.activity.url

    def process(self):
        from dashboard.models import Profile
        mr = self
        print("_")
        with transaction.atomic():
            mr.ranking.all().delete()
            data = get_eligible_input_data(mr)
            total_pot = mr.amount
            print(mr, f"{len(data)} earnings to process")
            results = []
            try:
                results = clr.run_calc(data, total_pot)
            except ZeroDivisionError:
                print('ZeroDivisionError; probably theres just not enough contribtuions in round')
            for result in results:
                try:
                    profile = Profile.objects.get(pk=result['id'])
                    match_curve = clr.run_live_calc(data, result['id'], 999999, total_pot)
                    contributors = len(set([ele[1] for ele in data if int(ele[0]) == profile.pk]))
                    contributions_for_this_user = [ele for ele in data if int(ele[0]) == profile.pk]
                    contributions = len(contributions_for_this_user)
                    contributions_total = sum([ele[2] for ele in contributions_for_this_user])
                    MatchRanking.objects.create(
                        profile=profile,
                        round=mr,
                        contributors=contributors,
                        contributions=contributions,
                        contributions_total=contributions_total,
                        match_total=result['clr_amount'],
                        match_curve=match_curve,
                        )
                except Exception as e:
                    if settings.DEBUG:
                        raise e

            # update number rankings
            number = 1
            for mri in mr.ranking.order_by('-match_total'):
                mri.number = number
                mri.save()
                number += 1


class MatchRanking(SuperModel):

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='match_rankings', blank=True)
    round = models.ForeignKey('townsquare.MatchRound',
        on_delete=models.CASCADE, related_name='ranking', blank=True, db_index=True)
    number = models.IntegerField(default=1)
    contributors = models.IntegerField(default=1)
    contributions = models.IntegerField(default=1)
    contributions_total = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    match_total = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    final = models.BooleanField(help_text='Is this match ranking final?', default=False)
    paid = models.BooleanField(help_text='Is this match ranking paikd?', default=False)
    payout_txid = models.CharField(max_length=255, default='', blank=True)
    payout_tx_status = models.CharField(max_length=255, default='', blank=True)
    payout_tx_issued = models.DateTimeField(db_index=True, null=True)
    match_curve = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Round {self.round.number}: Ranked {self.number}, {self.profile.handle} got {self.contributions} contributions worth ${self.contributions_total} for ${self.match_total} Matching"

    @property
    def default_match_estimate(self):
        # TODO: 0.3 is the defaul contribution amount, so we're pulling the match estimate
        return self.match_curve["0.3"] - float(self.match_total)

    @property
    def sorted_match_curve(self):
        # returns a dict of the amounts that new matching affect things
        import collections
        items = self.match_curve.items()
        items = [[float(ele[0]), ele[1] - float(self.match_total)] for ele in items]
        od = collections.OrderedDict(sorted(items))
        return od


def get_eligible_input_data(mr):
    from dashboard.models import Tip
    from django.db.models import Q, F
    from dashboard.models import Earning, Profile
    from django.contrib.contenttypes.models import ContentType
    network = 'mainnet'
    earnings = Earning.objects.filter(created_on__gt=mr.valid_from, created_on__lt=mr.valid_to)
    # filter out earnings that have invalid info (due to profile deletion), or dont have a USD value, or are not on the correct network
    earnings = earnings.filter(to_profile__isnull=False, from_profile__isnull=False, value_usd__isnull=False, network=network)
    # filter out staff earnings
    earnings = earnings.exclude(to_profile__user__is_staff=True)
    # filter out self earnings
    earnings = earnings.exclude(to_profile__pk=F('from_profile__pk'))
    # blacklisted users
    earnings = earnings.exclude(to_profile__pk=68768)
    # microtips only
    earnings = earnings.filter(source_type=ContentType.objects.get(app_label='dashboard', model='tip'))
    tips = list(Tip.objects.send_happy_path().filter(Q(comments_priv__contains='activity:') | Q(comments_priv__contains='comment:') | Q(tokenName='ETH', amount__lte=0.05)).values_list('pk', flat=True))
    earnings = earnings.filter(source_id__in=tips)
    # filter out colluding profiles
    excluded_profiles = SquelchProfile.objects.filter(active=True).values_list('profile__id', flat=True)
    earnings = earnings.exclude(to_profile__in=excluded_profiles)
    earnings = earnings.exclude(from_profile__in=excluded_profiles)

    # output
    earnings = earnings.values_list('to_profile__pk', 'from_profile__pk', 'value_usd')
    return [[ele[0], ele[1], float(ele[2])] for ele in earnings]

class SuggestedAction(SuperModel):

    title = models.CharField(max_length=50, blank=True)
    desc = models.TextField(default='', blank=True)
    suggested_donation = models.CharField(max_length=50, blank=True)
    matchpotential = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(help_text='Is this suggestion active?', default=True)
    rank = models.IntegerField(default=0, db_index=True)

    def __str__(self):
        return f"{self.title} / {self.suggested_donation}"


class Favorite(SuperModel):
    """Model for each favorite."""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='favorites')
    grant = models.ForeignKey('grants.Grant', on_delete=models.CASCADE, related_name='grant_favorites', null=True)
    activity = models.ForeignKey('dashboard.Activity', on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now=True)

    @staticmethod
    def grants():
        return Favorite.objects.filter(activity=None)

    def __str__(self):
        return f"Favorite {self.activity.activity_type}:{self.activity_id} by {self.user}"


class PinnedPost(SuperModel):
    """Model for each Pinned Post."""

    user = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='pins')
    activity = models.ForeignKey('dashboard.Activity',
        on_delete=models.CASCADE, related_name='pin')
    what = models.CharField(max_length=100, default='', unique=True)
    created = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Pin {self.activity.activity_type} by {self.user}"

    @property
    def url(self):
        return self.activity.url

    def get_absolute_url(self):
        return self.activity.url


class SquelchProfile(SuperModel):
    """Squelches a profile from earning in CLR"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='squelches')
    comments = models.TextField(default='', blank=True)
    active = models.BooleanField(help_text='Is squelch applied?', default=True)

    def __str__(self):
        return f"SquelchProfile {self.profile.handle} => {self.comments}"
