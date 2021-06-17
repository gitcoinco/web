# -*- coding: utf-8 -*-
"""Define the quadraticlands views.

Copyright (C) 2020 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

from app.utils import get_upload_filename
from economy.models import SuperModel
from django.contrib.postgres.fields import ArrayField, JSONField
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from dashboard.models import Profile


class Uint256Field(models.DecimalField):
    description = _("Ethereum uint256 number")
    '''
    Field to store ethereum uint256 values. Uses Decimal db type without decimals to store
    in the database, but retrieve as `int` instead of `Decimal` (https://docs.python.org/3/library/decimal.html)
    https://github.com/gnosis/gnosis-py/blob/master/gnosis/eth/django/models.py
    '''
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 79  # 2 ** 256 is 78 digits
        kwargs['decimal_places'] = 0
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_digits']
        del kwargs['decimal_places']
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return int(value)

class QuadLandsFAQ(models.Model):
    '''Table for storing quadlands FAQ items'''
    position = models.IntegerField(
        blank=False, 
        unique=True
    )
    created_on = models.DateTimeField(
        auto_now=True
    )
    question = models.TextField(
        default='', 
        blank=True
    )
    answer = models.TextField(
        default='', 
        blank=True
    )
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.question}'

class InitialTokenDistribution(models.Model):
    '''Table for storing the initial gitcoin retroactive token distribution details'''
    profile = models.ForeignKey(
        'dashboard.Profile', 
        related_name='initial_distribution', 
        on_delete=models.CASCADE
    ) 
    created_on = models.DateTimeField(
        auto_now=True
    )
    claim_total = Uint256Field(
        default=0
    )
    distribution = JSONField(
        default=dict
    )
    
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.profile.handle}, {self.claim_total}, {self.created_on}, {self.distribution}'

class QLVote(models.Model):
    '''Store signed messages and vote data for QL initial dist vote'''
    profile = models.ForeignKey(
        'dashboard.Profile', 
        related_name='vote_status',
        on_delete=models.CASCADE
    )
    signature = models.CharField(
        default='',
        max_length=255,
    )
    vote = JSONField(
        default=dict
    )
    full_msg = JSONField(
        default=dict
    )
    created_on = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.profile.handle}, {self.signature}, {self.vote}, {self.created_on}'


class MissionStatus(models.Model):
    ''' Track which missions a given user has completed'''
    profile = models.ForeignKey(
        'dashboard.Profile', 
        related_name='mission_status', 
        on_delete=models.CASCADE
    )
    proof_of_use = models.BooleanField(
        default=False
    )
    proof_of_receive = models.BooleanField(
        default=False
    )
    proof_of_knowledge = models.BooleanField(
        default=False
    )
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.profile.handle}, {self.proof_of_use}, {self.proof_of_receive}, {self.proof_of_knowledge}'

class GTCSteward(models.Model):
    '''Store data for Gitcoin Stewards'''
    profile = models.ForeignKey(
        'dashboard.Profile', 
        related_name='GTCSteward', 
        on_delete=models.CASCADE
    )
    real_name = models.CharField(
        default=False, 
        max_length=50
    )
    bio = models.CharField(
        default=False, 
        max_length=64
    )
    gtc_address = models.CharField(
        default='0x0',
        max_length=255,
    )
    profile_link = models.URLField(
        default=False, 
        max_length=255
    )
    custom_steward_img = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('override steward image as opposed to profile avatar'),
    )
    
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.profile.handle}, {self.real_name}, {self.bio}, {self.gtc_address}, {self.profile_link}'


class SchwagCoupon(models.Model):
    '''Coupon Code for users who have completed missions'''
    DISCOUNT_TYPE = [
        ('20_off', '20 OFF'),
        ('40_off', '40 OFF'),
        ('60_off', '60 OFF'),
    ]
    profile = models.ForeignKey(
        'dashboard.Profile', 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_('profile which has claimed the coupon'),
    )
    coupon_code = models.CharField(
        default=False, 
        max_length=20,
        help_text=_('actual coupon code'),
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE,
        help_text="discount"
    )

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.discount_type}, {self.coupon_code}, {self.profile}'

def create_game_helper(handle, title):
    game = Game.objects.create(
        _type = 'diplomacy',
        title = title,
        )
    player = GamePlayer.objects.create(
        game = game,
        profile = Profile.objects.get(handle=handle),
        active = True,
        admin = True
        )
    game.players.add(player)

    GameFeed.objects.create(
            game=game,
            player=player,
            data={
                'action': 'created the game',
            },
            )
    game.add_player(player.profile.handle)
    return game

class Game(SuperModel):

    title = models.CharField(max_length=500, blank=True)
    _type = models.CharField(
        default='',
        db_index=True,
        max_length=255,
    )
    uuid=models.UUIDField(default=uuid.uuid4, unique=True)
    slug = AutoSlugField(populate_from='title')

    def players_text(self):
        return ", ".join([player.profile.handle for player in self.players.all()])

    def get_absolute_url(self):
        return f'/quadraticlands/mission/diplomacy/{self.uuid}/{self.slug}'
    
    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def gtc_used(self):
        return self.current_votes_total

    @property
    def sybil_created(self):
        amount = self.current_votes_total * 0.007 # estimate of the GTC to trust bonus ratio
        return amount

    def is_active_player(self, handle):
        return self.active_players.filter(profile__handle=handle).exists()

    def add_player(self, handle):
        profile = Profile.objects.get(handle=handle)
        if not self.is_active_player(handle):
            GamePlayer.objects.create(profile=profile, active=True, game=game)

        return GameFeed.objects.create(
            game=self,
            player=self.players.get(profile__handle=handle),
            data={
                'action': 'joined',
            },
            )

    def remove_player(self, handle):
        player = self.players.filter(profile__handle=handle).first()
        player.active = False
        player.save()

        return GameFeed.objects.create(
            game=self,
            player=self.players.get(profile__handle=handle),
            data={
                'action': 'left the game',
            },
            )

        if player.admin:
            player.admin = False 
            player.save()

            # promote someone new to admin
            self.promote_admin()

    def promote_admin(self):
        if not self.active_players.exists():
            return False

        player = self.active_players.first()
        return GameFeed.objects.create(
            game=self,
            player=player,
            data={
                'action': 'was promoted to admin',
            },
            )

    def make_move(self, handle, package):

        return GameFeed.objects.create(
            game=self,
            player=self.players.get(profile__handle=handle),
            data={
                'action': 'vouched',
                'package': package,
            },
            )

    def chat(self, handle, chat):

        return GameFeed.objects.create(
            game=self,
            player=self.players.get(profile__handle=handle),
            data={
                'action': 'chatted',
                'chat': chat,
            },
            )
    
    def leave_game(self, handle):

        return GameFeed.objects.create(
            game=self,
            player=self.players.get(profile__handle=handle),
            data={
                'action': 'left the game',
            },
            )

    def __str__(self):
        return self.title


    @property
    def admin(self):
        return self.players.filter(admin=True).first()

    @property
    def current_votes_total(self):
        return sum(player.tokens_in for player in self.active_players.all())

    @property
    def active_players(self):
        return self.players.filter(active=True)


@receiver(pre_save, sender=Game, dispatch_uid="psave_game")
def psave_game(sender, instance, **kwargs):
    pass

class GameFeed(SuperModel):

    game = models.ForeignKey(
        'quadraticlands.Game',
        related_name='feed',
        null=True,
        on_delete=models.CASCADE,
        help_text=_('Link to Game')
    )
    player = models.ForeignKey(
        'quadraticlands.GamePlayer',
        related_name='game_feed',
        on_delete=models.CASCADE,
        help_text=_('The game feed update creators\'s profile.'),
        null=True,
    )
    data = JSONField(default=dict)


    def __str__(self):
        return f"{self.game}, {self.player.profile.handle}: {self.data}"

    def votes(self):
        if self.data['action'] != 'vouched':
            return []
        return self.data.get('package',{}).get('moves',{}).get('votes',[])

class GamePlayer(SuperModel):

    game = models.ForeignKey(
        'quadraticlands.Game',
        related_name='players',
        on_delete=models.CASCADE,
        help_text=_('The Game')
    )
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='players',
        on_delete=models.CASCADE,
        help_text=_('The player of the game.'),
    )
    admin = models.BooleanField(
        default=False
    )
    active = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.game} / {self.profile.handle} / Admin: {self.admin} / Active: {self.active}"

    @property
    def last_action(self):
        return self.game.feed.filter(player=self).order_by('-created_on').first()

    @property
    def last_move(self):
        return self.game.feed.filter(player=self, data__action='vouched').order_by('-created_on').first()

    def votes(self):
        if self.data['action'] != 'vouched':
            return []
        return self.data.get('package',{}).get('moves',{}).get('votes',[])


    @property
    def votes_in(self):
        return_dict = {

        }
        for player in self.game.active_players:
            return_dict[player.profile.handle] = 0
            last_move = player.last_move
            if last_move:
                for vote in last_move.votes():
                    if vote['username'] == self.profile.handle:
                        return_dict[player.profile.handle] += float(vote['value'])
        return return_dict

    @property
    def tokens_in(self):
        return sum(ele for key, ele in self.votes_in.items())

    @property
    def tokens_out(self):
        if not self.last_move:
            return 0
        return sum(float(ele['value']) for ele in self.last_move.votes())