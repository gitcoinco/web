from django.db import models

# Create your models here.
from economy.models import SuperModel
from django.contrib.postgres.fields import ArrayField, JSONField
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from dashboard.models import Profile

class Game(SuperModel):

    invite_codes = JSONField(default=dict)
    gameboard = JSONField(default=dict)
    setup = JSONField(default=dict)
    title = models.TextField(max_length=500, blank=True)
    slug = AutoSlugField(populate_from='title')
    creator = models.ForeignKey(
        'dashboard.Profile',
        related_name='game_created',
        on_delete=models.CASCADE,
        help_text=_('The game administrator\'s profile.'),
        null=True,
    )

    def to_game_config(self, profile):
        return {
          'pk': self.pk,
          'slug': self.slug,
          'room_name': self.title,
          'allocation': self.allocation,
          'this_player': profile.handle,
          'players_to_seats': self.players,
          'gameboard': self.gameboard,
        }

    def get_absolute_url(self):
        return f'/governance/quadratic-diplomacy/{self.slug}'

    def add_player(self, handle):
        if handle in self.players:
            return False
        self.setup['players'].append(handle)
        new_size = len(self.gameboard[0])
        for i in range(0, new_size):
            self.gameboard[i].append(0)
        self.gameboard.append([0 for i in range(new_size + 1)])

        return GameFeed.objects.create(
            game=self,
            sender=Profile.objects.get(handle=handle),
            data={
                'type': 'joined',
            },
            )

    def __str__(self):
        return self.title

    @property
    def players(self):
        return self.setup.get('players', [])

    @property
    def allocation(self):
        return self.setup.get('allocation', 100)

    def handle_to_idx(self, handle):
        for i in range(0, len(self.players)):
            if self.players[i] == handle:
                return i
        return None

    def handle_to_allocation(self, handle):
        idx = self.handle_to_idx(handle)
        if idx == None:
            return False
        num = 0
        for item in self.gameboard[idx]:
            num += item
        return num

    def play_move(self, handle, i, j, new_vote):
        idx = self.handle_to_idx(handle)
        if idx == None:
            return False
        if idx != i:
            return False
        old_vote = self.gameboard[i][j]

        self.gameboard[i][j] = new_vote
        if self.handle_to_allocation(handle) > self.allocation:
            self.gameboard[i][j] = old_vote
            return False

        return GameFeed.objects.create(
            game=self,
            sender=Profile.objects.get(handle=handle),
            data={
                'type': 'move',
                'old_vote': old_vote,
                'new_vote': new_vote,
                'where': [i, j],
            },
            )

    def message(self, handle, message):
        if handle not in self.players:
            return False
        return GameFeed.objects.create(
            game=self,
            sender=Profile.objects.get(handle=handle),
            data={
                'type': 'msg',
                'message': message,
            },
            )



@receiver(pre_save, sender=Game, dispatch_uid="psave_game")
def psave_game(sender, instance, **kwargs):
    if 'players' not in instance.setup.keys():
        instance.setup['players'] = {}

class GameFeed(SuperModel):

    game = models.ForeignKey(
        'governance.Game',
        related_name='feed',
        null=True,
        on_delete=models.CASCADE,
        help_text=_('Link to Game')
    )
    sender = models.ForeignKey(
        'dashboard.Profile',
        related_name='game_feed',
        on_delete=models.CASCADE,
        help_text=_('The game feed update creators\'s profile.'),
        null=True,
    )
    data = JSONField(default=dict)

    @property
    def message(self):
        msg = f'[{self.created_on.strftime("%H:%M")}]'
        if self.data['type'] == 'msg':
            msg += f"{self.sender.handle}: {self.data['message']}"
        if self.data['type'] == 'move':
            msg += f"{self.sender.handle} moved {self.game.players[self.data['where'][1]]} from {self.data['old_vote']} to {self.data['new_vote']}"
        if self.data['type'] == 'joined':
            msg += f"{self.sender.handle} has joined the game"
        return msg

