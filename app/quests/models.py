import random

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.
from economy.models import SuperModel
from unidecode import unidecode

num_backgrounds = 34
video_enabled_backgrounds = [4, 6, 8, 9, 10, 11, 13, 14, 22, 23, 34]


class Quest(SuperModel):
    DIFFICULTIES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Hard', 'Hard'),
        ('Expert', 'Expert'),
    ]

    BACKGROUNDS = [
        ('red', 'red'),
        ('green', 'green'),
        ('blue', 'blue'),
    ] + [(f'back{i}', f'back{i}') for i in range(0, num_backgrounds + 1)]

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
    reward_tip = models.ForeignKey('dashboard.Tip', blank=True, null=True, related_name='quests_reward_token', on_delete=models.SET_NULL)
    unlocked_by_quest = models.ForeignKey('quests.Quest', blank=True, null=True, related_name='unblocks_quest', on_delete=models.SET_NULL)
    unlocked_by_hackathon = models.ForeignKey('dashboard.HackathonEvent', blank=True, null=True, related_name='unblocks_quest', on_delete=models.SET_NULL)
    cooldown_minutes = models.IntegerField(default=5)
    visible = models.BooleanField(default=True, db_index=True)
    force_visible = models.BooleanField(default=False, help_text='override such that the re_rank_quests mgmt command does not make the quest invisible due to low feedback.')
    difficulty = models.CharField(max_length=100, default='Beginner', choices=DIFFICULTIES, db_index=True)
    style = models.CharField(max_length=100, default='quiz', choices=STYLES)
    value = models.FloatField(default=1)
    background = models.CharField(default='', max_length=100, blank=True, choices=BACKGROUNDS)
    creator = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='quests_created',
        null=True,
        blank=True,
    )
    ui_data = JSONField(default=dict, blank=True)
    edit_comments = models.TextField(default='', blank=True)
    admin_comments = models.TextField(default='', blank=True)

    def __str__(self):
        """Return the string representation of this obj."""
        return f'{self.pk}, {self.title} (visible: {self.visible})'

    @property
    def url(self):
        from django.conf import settings
        return settings.BASE_URL + self.relative_url

    @property
    def video(self):
        return self.game_metadata.get('video', None)

    @property
    def relative_url(self):
        return f"quests/{self.pk}/{slugify(unidecode(self.title))}"

    @property
    def edit_url(self):
        from django.conf import settings
        return settings.BASE_URL + f"quests/edit/{self.pk}"

    @property
    def feedback_url(self):
        from django.conf import settings
        return settings.BASE_URL + f"quests/{self.pk}/feedback"

    @property
    def feedbacks(self):
        stats = {1 : 0, -1 : 0, 0 : 0}
        for fb in self.feedback.all():
            stats[fb.vote] += 1
        ratio_upvotes = 0
        if self.feedback.count():
            ratio_upvotes = stats[1]/self.feedback.count()
        return_me = {
            'ratio': ratio_upvotes,
            'stats': stats,
            'feedback': []
        }
        for fb in self.feedback.all():
            return_me['feedback'].append(fb.comment)
        return return_me

    @property
    def est_read_time_mins(self):
        return self.game_schema.get('est_read_time_mins', 10)

    @property
    def is_dead_end(self):
        """
        returns True IFF the quest has a question for which there is no possible winning path

        """
        is_dead_end = False
        for question in self.questions:
            is_this_question_dead_end = not any(ele['correct'] for ele in question['responses'])
            if is_this_question_dead_end:
                is_dead_end = True
        return is_dead_end

    @property
    def est_skim_time_mins(self):
        return round(int(self.est_read_time_mins) / 5)

    @property
    def est_total_time_required(self):
        return self.est_read_time_mins

    def get_absolute_url(self):
        return self.url

    @property
    def art_url(self):
        url = self.game_metadata.get('enemy', {}).get('art', '')
        if "http" in url:
            return url
        return '/static/' + url

    @property
    def enemy_img_url(self):
        return self.art_url

    @property
    def enemy_img_url_png(self):
        # warning: not supported for kudos uploaded quets
        return self.art_url.replace('svg', 'png')

    @property
    def avatar_url_png(self):
        # warning: not supported for kudos uploaded quets
        if self.kudos_reward:
            return self.kudos_reward.img_url
        return self.art_url.replace('svg', 'png')

    @property
    def enemy_img_name(self):
        return '/static/'+self.game_metadata.get('enemy', {}).get('title', '')

    @property
    def assign_background(self):
        if self.background:
            return self.background
        backgrounds = list(range(0, num_backgrounds + 1))
        which_back_idx = random.choice(backgrounds)
        if self.pk:
            which_back_idx = self.pk % len(backgrounds)
        which_back = backgrounds[which_back_idx]
        return f"back{which_back}"

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
            self.style,
        ]
        if (timezone.now() - self.created_on).days < 5:
            tags.append('new')
        if self.attempts.count() > 400:
            tags.append('popular')

        return tags


    @property
    def success_pct(self):
        attempts = self.attempts.count()
        if not attempts:
            return 0
        return round(self.success_count * 100 / attempts)

    def is_unlocked_for(self, user):
        if not self.unlocked_by_quest and not self.unlocked_by_hackathon:
            return True

        if not user.is_authenticated:
            return False

        is_unlocked = False
        if self.unlocked_by_quest:
            is_unlocked = user.profile.quest_attempts.filter(success=True, quest=self.unlocked_by_quest).exists()

        if self.unlocked_by_hackathon:
            from dashboard.models import HackathonRegistration
            is_unlocked = HackathonRegistration.objects.filter(hackathon=self.unlocked_by_hackathon, registrant=user.profile).exists()
        return is_unlocked


    def is_beaten(self, user):
        if not user.is_authenticated:
            return False

        is_completed = user.profile.quest_attempts.filter(success=True, quest=self).exists()
        return is_completed

    def questions_safe(self, idx):
        # strips out all correctness repsonses so that the client may see the question
        # without being able to see the answer
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


@receiver(pre_save, sender=Quest, dispatch_uid="psave_quest")
def psave_quest(sender, instance, **kwargs):
    if not instance.background:
        instance.background = instance.assign_background
    instance.ui_data['attempts_count'] = instance.attempts.count()
    instance.ui_data['tags'] = instance.tags
    instance.ui_data['success_pct'] = instance.success_pct
    instance.ui_data['feedbacks'] = instance.feedbacks
    instance.ui_data['creator'] = {
        'url': instance.creator.url,
        'handle': instance.creator.handle,
    }

    from django.contrib.contenttypes.models import ContentType
    from search.models import SearchResult
    if instance.pk:
        SearchResult.objects.update_or_create(
            source_type=ContentType.objects.get(app_label='quests', model='quest'),
            source_id=instance.pk,
            defaults={
                "created_on":instance.created_on,
                "title":instance.title,
                "description":instance.description,
                "url":instance.url,
                "visible_to":None,
                'img_url': instance.enemy_img_url,
            }
            )



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


class QuestFeedback(SuperModel):

    quest = models.ForeignKey('quests.Quest', blank=True, null=True, related_name='feedback', on_delete=models.SET_NULL)
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='quest_feedback',
    )
    vote = models.IntegerField(default=1)
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        """Return the string representation of this obj."""
        handle = self.profile.handle if self.profile else 'deleted profile'
        title = self.quest.title if self.quest else 'deleted quest'
        return f'{self.pk}, {self.profile.handle} => {title} ({self.comment})'


class QuestPointAward(SuperModel):

    questattempt = models.ForeignKey('quests.QuestAttempt', related_name='pointawards', on_delete=models.CASCADE)
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='questpointawards',
    )
    value = models.FloatField()
    action = models.CharField(max_length=100, default='Beat')
    round_number = models.IntegerField(default=1)
    metadata = JSONField(default=dict, blank=True)

    def __str__(self):
        """Return the string representation of this obj."""
        return f'{self.value}, {self.profile.handle}'

@receiver(pre_save, sender=QuestPointAward, dispatch_uid="psave_point")
def psave_point(sender, instance, **kwargs):
    has_quest = instance.questattempt and instance.questattempt.quest
    instance.metadata = {
        'enemy_img' : instance.questattempt.quest.enemy_img_url if has_quest else None,
        'quest_url' : instance.questattempt.quest.url  if has_quest else None,
        'handle' : instance.profile.handle if instance.profile else None,
        'title' : instance.questattempt.quest.title if has_quest else None,
    }
