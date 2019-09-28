from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.
from economy.models import SuperModel


class Quest(SuperModel):
    title = models.CharField(max_length=1000)
    description = models.TextField(default='', blank=True)
    game_schema = JSONField(default=dict, blank=True)
    game_metadata = JSONField(default=dict, blank=True)
    questions = JSONField(default=dict, blank=True)
    kudos_reward = models.ForeignKey('kudos.Token', blank=True, null=True, related_name='quests_reward', on_delete=models.SET_NULL)
    unlocked_by = models.ForeignKey('quests.Quest', blank=True, null=True, related_name='unblocks', on_delete=models.SET_NULL)
    cooldown_minutes = models.IntegerField(default=5)
    visible = models.BooleanField(default=True)

    def __str__(self):
        """Return the string representation of this obj."""
        return f'{self.pk}, {self.title}'


    @property
    def url(self):
        return f"/quests/{self.pk}/{slugify(self.title)}"


    @property
    def enemy_img_url(self):
        return '/static/'+self.game_metadata.get('enemy', {}).get('art', '').replace('svg', 'png')

    @property
    def background(self):
        backgrounds = [
            'camping',
            'back_city',
            'city',
            'night',
        ]
        which_back = self.pk % len(backgrounds)
        return backgrounds[which_back]

    @property
    def success_count(self):
        return self.attempts.filter(success=True).count()

    def is_unlocked_for(self, user):
        if not self.unlocked_by:
            return True

        if not user.is_authenticated:
            return False

        is_completed = user.profile.quest_attempts.filter(success=True, quest=self.unlocked_by).exists()
        return is_completed


    def is_beaten(self, user):
        if not user.is_authenticated:
            return False

        is_completed = user.profile.quest_attempts.filter(success=True, quest=self).exists()
        return is_completed

    def questions_safe(self, idx):
        try:
            question = self.questions[idx]
            num_responses = question['responses']
            for i in range(0, len(num_responses)):
                del question['responses'][i]['correct']
            return question
        except:
            return None


    def is_within_cooldown_period(self, user):
        if not user.is_authenticated:
            return False

        cooldown_period_mins = self.cooldown_minutes
        is_completed = user.profile.quest_attempts.filter(success=False, quest=self, created_on__gt=(timezone.now() - timezone.timedelta(minutes=cooldown_period_mins))).exists()
        return is_completed

        


class QuestAttempt(SuperModel):

    quest = models.ForeignKey('quests.Quest', blank=True, null=True, related_name='attempts', on_delete=models.SET_NULL)
    success = models.BooleanField(default=False)
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='quest_attempts',
    )
    state = models.IntegerField(default=0)

    def __str__(self):
        """Return the string representation of this obj."""
        return f'{self.pk}, {self.profile.handle} => {self.quest.title} state: {self.state} success: {self.success}'
