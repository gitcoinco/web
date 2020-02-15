from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models.signals import post_save
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
    likes = ArrayField(models.IntegerField(), default=list, blank=True) #pks of users who like this post

    def __str__(self):
        return f"Comment of {self.activity.pk} by {self.profile.handle}: {self.comment}"

    @property
    def profile_handle(self):
        return self.profile.handle

    @property
    def url(self):
        return self.activity.url

    @property
    def tip_count_eth(self):
        from dashboard.models import Tip
        network = 'rinkeby' if settings.DEBUG else 'mainnet'
        tips = Tip.objects.filter(comments_priv=f"comment:{self.pk}", network=network)
        return sum([tip.value_in_eth for tip in tips])

    def get_absolute_url(self):
        return self.url


@receiver(post_save, sender=Comment, dispatch_uid="post_save_comment")
def postsave_comment(sender, instance, created, **kwargs):
    from townsquare.tasks import send_comment_email
    send_comment_email.delay(instance.pk)


class OfferQuerySet(models.QuerySet):
    """Handle the manager queryset for Offers."""

    def current(self):
        """Filter results down to current offers only."""
        return self.filter(valid_from__lte=timezone.now(), valid_to__gt=timezone.now(), public=True)

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
            results = clr.run_calc(data, total_pot)
            for result in results:
                try:
                    profile = Profile.objects.get(pk=result['id'])
                    contributions_by_this_user = [ele for ele in data if int(ele[0]) == profile.pk]
                    contributions = len(contributions_by_this_user)
                    contributions_total = sum([ele[2] for ele in contributions_by_this_user])
                    MatchRanking.objects.create(
                        profile=profile,
                        round=mr,
                        contributions=contributions,
                        contributions_total=contributions_total,
                        match_total=result['clr_amount'],
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
    contributions = models.IntegerField(default=1)
    contributions_total = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    match_total = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    final = models.BooleanField(help_text='Is this match ranking final?', default=False)
    paid = models.BooleanField(help_text='Is this match ranking paikd?', default=False)
    payout_txid = models.CharField(max_length=255, default='', blank=True)
    payout_tx_status = models.CharField(max_length=255, default='', blank=True)
    payout_tx_issued = models.DateTimeField(db_index=True, null=True)

    def __str__(self):
        return f"Round {self.round.number}: Ranked {self.number}, {self.profile.handle} got {self.contributions} contributions worth ${self.contributions_total} for ${self.match_total} Matching"


def get_eligible_input_data(mr):
    from dashboard.models import Earning, Profile
    network = 'mainnet' if not settings.DEBUG else 'rinkeby'
    earnings = Earning.objects.filter(created_on__gt=mr.valid_from, created_on__lt=mr.valid_to)
    earnings = earnings.filter(to_profile__isnull=False, from_profile__isnull=False, value_usd__isnull=False, network=network)
    earnings = earnings.exclude(to_profile__user__is_staff=True)
    earnings = earnings.values_list('to_profile__pk', 'from_profile__pk', 'value_usd')
    return [[ele[0], ele[1], float(ele[2])] for ele in earnings]
