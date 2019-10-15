from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.
from economy.models import SuperModel


class Quest(SuperModel):
    DIFFICULTIES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    STYLES = [
        ('Quiz', 'quiz'),
        ('Example for Demo', 'example_demo'),
    ]

    title = models.CharField(max_length=1000)
    description = models.TextField(default='', blank=True)
    game_schema = JSONField(default=dict, blank=True)
    game_metadata = JSONField(default=dict, blank=True)
    questions = JSONField(default=dict, blank=True)
    kudos_reward = models.ForeignKey('kudos.Token', blank=True, null=True, related_name='quests_reward', on_delete=models.SET_NULL)
    unlocked_by = models.ForeignKey('quests.Quest', blank=True, null=True, related_name='unblocks', on_delete=models.SET_NULL)
    cooldown_minutes = models.IntegerField(default=5)
    visible = models.BooleanField(default=True, db_index=True)
    difficulty = models.CharField(max_length=100, default='Beginner', choices=DIFFICULTIES, db_index=True)
    style = models.CharField(max_length=100, default='quiz', choices=STYLES)
    value = models.FloatField(default=1)
    creator = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='quests_created',
        null=True,
        blank=True,
    )

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
    def enemy_img_name(self):
        return '/static/'+self.game_metadata.get('enemy', {}).get('title', '')

    @property
    def background(self):
        backgrounds = [
            'back0',
            'back1',
            'back2',
            'back3',
        ]
        which_back = self.pk % len(backgrounds)
        return backgrounds[which_back]

    @property
    def music(self):
        musics = [
            'boss-battle',
            'boss-battle1',
            'boss-battle2',
            'boss-battle3',
            'boss-battle4',
        ]
        idx = self.pk % len(musics)
        return musics[idx]

    @property
    def success_count(self):
        return self.attempts.filter(success=True).count()

    @property
    def tags(self):
        tags = [
            self.difficulty,
            "hard" if self.success_pct < 20 else ( "medium" if self.success_pct < 70 else "easy"),
        ]
        if (timezone.now() - self.created_on).days < 5:
            tags.append('new')
        if self.attempts.count() > 40:
            tags.append('popular')

        return tags


    @property
    def success_pct(self):
        attempts = self.attempts.count()
        if not attempts:
            return 0
        return round(self.success_count * 100 / attempts)

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

    def last_failed_attempt(self, user):
        if not user.is_authenticated:
            return False

        return user.profile.quest_attempts.filter(success=False).order_by('-pk').first()


class QuestAttempt(SuperModel):

    quest = models.ForeignKey('quests.Quest', blank=True, null=True, related_name='attempts', on_delete=models.SET_NULL)
    success = models.BooleanField(default=False, db_index=True)
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='quest_attempts',
    )
    state = models.IntegerField(default=0)

    def __str__(self):
        """Return the string representation of this obj."""
        return f'{self.pk}, {self.profile.handle} => {self.quest.title} state: {self.state} success: {self.success}'

class QuestPointAward(SuperModel):

    questattempt = models.ForeignKey('quests.QuestAttempt', related_name='pointawards', on_delete=models.CASCADE)
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='questpointawards',
    )
    value = models.FloatField()

    def __str__(self):
        """Return the string representation of this obj."""
        return f'{self.value}, {self.profile.handle}'
